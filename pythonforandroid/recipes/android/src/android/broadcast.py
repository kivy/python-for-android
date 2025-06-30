# -------------------------------------------------------------------
# Broadcast receiver bridge for Kivy + Pyjnius
# Safe start/stop with Android lifecycle integration
# -------------------------------------------------------------------

from jnius import autoclass, PythonJavaClass, java_method
from android.config import JAVA_NAMESPACE, JNI_NAMESPACE, ACTIVITY_CLASS_NAME, SERVICE_CLASS_NAME


class BroadcastReceiver:
    class Callback(PythonJavaClass):
        __javainterfaces__ = [JNI_NAMESPACE + '/GenericBroadcastReceiverCallback']
        __javacontext__ = 'app'

        def __init__(self, callback, *args, **kwargs):
            self.callback = callback
            super().__init__(*args, **kwargs)

        @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
        def onReceive(self, context, intent):
            self.callback(context, intent)

    def __init__(self, callback, actions=None, categories=None):
        if not actions and not categories:
            raise Exception('You need to define at least actions or categories')

        self.callback = callback
        self._is_registered = False
        self._handlerthread_started = False

        # Expand intent names
        Intent = autoclass('android.content.Intent')

        def _expand(partial):
            if '.' in partial:
                return partial
            name = 'ACTION_' + partial.upper()
            if not hasattr(Intent, name):
                raise Exception(f'Intent {name} does not exist')
            return getattr(Intent, name)

        self.resolved_actions = [_expand(a) for a in actions or []]
        self.resolved_categories = [_expand(c) for c in categories or []]

        # Java classes
        self.GenericBroadcastReceiver = autoclass(JAVA_NAMESPACE + '.GenericBroadcastReceiver')
        self.IntentFilter = autoclass('android.content.IntentFilter')
        self.Handler = autoclass('android.os.Handler')
        self.HandlerThreadClass = autoclass('android.os.HandlerThread')

        # Build filter
        self.receiver_filter = self.IntentFilter()
        for action in self.resolved_actions:
            self.receiver_filter.addAction(action)
        for category in self.resolved_categories:
            self.receiver_filter.addCategory(category)

        # Receiver and callback
        self.listener = BroadcastReceiver.Callback(self.callback)
        self.receiver = self.GenericBroadcastReceiver(self.listener)

        # Init thread placeholder
        self.handlerthread = None
        self.handler = None

    def start(self):
        if self._is_registered:
            print("[BroadcastReceiver] Already registered.")
            return

        if not self._handlerthread_started:
            self.handlerthread = self.HandlerThreadClass('BroadcastReceiverThread')
            try:
                self.handlerthread.start()
                self._handlerthread_started = True
            except Exception as e:
                print(f"[BroadcastReceiver] HandlerThread start failed: {e}")
                return

        try:
            self.handler = self.Handler(self.handlerthread.getLooper())
            self.context.registerReceiver(self.receiver, self.receiver_filter, None, self.handler)
            self._is_registered = True
            print("[BroadcastReceiver] Registered.")
        except Exception as e:
            print(f"[BroadcastReceiver] registerReceiver failed: {e}")

    def stop(self):
        if self._is_registered:
            try:
                self.context.unregisterReceiver(self.receiver)
                print("[BroadcastReceiver] Unregistered.")
            except Exception as e:
                print(f"[BroadcastReceiver] unregisterReceiver failed: {e}")
            self._is_registered = False

        if self._handlerthread_started:
            try:
                self.handlerthread.quitSafely()
                print("[BroadcastReceiver] HandlerThread quit safely.")
            except Exception as e:
                print(f"[BroadcastReceiver] thread quit failed: {e}")
            self._handlerthread_started = False
            self.handlerthread = None
            self.handler = None

    @property
    def context(self):
        from os import environ
        if 'PYTHON_SERVICE_ARGUMENT' in environ:
            PythonService = autoclass(SERVICE_CLASS_NAME)
            return PythonService.mService
        PythonActivity = autoclass(ACTIVITY_CLASS_NAME)
        return PythonActivity.mActivity
