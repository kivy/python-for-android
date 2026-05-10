# -------------------------------------------------------------------
# Broadcast receiver bridge
import logging
from jnius import autoclass, PythonJavaClass, java_method
from android.config import JAVA_NAMESPACE, JNI_NAMESPACE, ACTIVITY_CLASS_NAME, SERVICE_CLASS_NAME

logger = logging.getLogger("BroadcastReceiver")
logger.setLevel(logging.DEBUG)


class BroadcastReceiver(object):

    class Callback(PythonJavaClass):
        __javainterfaces__ = [JNI_NAMESPACE + '/GenericBroadcastReceiverCallback']
        __javacontext__ = 'app'

        def __init__(self, callback, *args, **kwargs):
            self.callback = callback
            PythonJavaClass.__init__(self, *args, **kwargs)

        @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
        def onReceive(self, context, intent):
            self.callback(context, intent)

    def __init__(self, callback, actions=None, categories=None):
        super().__init__()
        self.callback = callback
        self._is_registered = False

        if not actions and not categories:
            raise Exception('You need to define at least actions or categories')

        def _expand_partial_name(partial_name):
            if '.' in partial_name:
                return partial_name  # Its actually a full dotted name
            else:
                name = 'ACTION_{}'.format(partial_name.upper())
                if not hasattr(Intent, name):
                    raise Exception('The intent {} does not exist'.format(name))
                return getattr(Intent, name)

        # resolve actions/categories first
        Intent = autoclass('android.content.Intent')
        resolved_actions = [_expand_partial_name(x) for x in actions or []]
        resolved_categories = [_expand_partial_name(x) for x in categories or []]

        # resolve android API
        GenericBroadcastReceiver = autoclass(JAVA_NAMESPACE + '.GenericBroadcastReceiver')
        IntentFilter = autoclass('android.content.IntentFilter')
        HandlerThread = autoclass('android.os.HandlerThread')

        # create a thread for handling events from the receiver
        self.handlerthread = HandlerThread('handlerthread')

        # create a listener
        self.listener = BroadcastReceiver.Callback(self.callback)
        self.receiver = GenericBroadcastReceiver(self.listener)
        self.receiver_filter = IntentFilter()
        for x in resolved_actions:
            self.receiver_filter.addAction(x)
        for x in resolved_categories:
            self.receiver_filter.addCategory(x)

    def start(self):

        if hasattr(self, 'handlerthread') and self.handlerthread.isAlive():
            logger.debug("HandlerThread already running, skipping start")
            return

        HandlerThread = autoclass('android.os.HandlerThread')
        self.handlerthread = HandlerThread('handlerthread')
        self.handlerthread.start()

        if self._is_registered:
            logger.info("Already registered.")
            return

        Handler = autoclass('android.os.Handler')
        self.handler = Handler(self.handlerthread.getLooper())
        self.context.registerReceiver(
            self.receiver, self.receiver_filter, None, self.handler)
        self._is_registered = True

    def stop(self):
        try:
            self.context.unregisterReceiver(self.receiver)
            self._is_registered = False
        except Exception as e:
            logger.error("unregisterReceiver failed: %s", e)

        if hasattr(self, 'handlerthread'):
            self.handlerthread.quitSafely()
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
