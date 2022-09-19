from jnius import PythonJavaClass, autoclass, java_method
from android.config import ACTIVITY_CLASS_NAME, ACTIVITY_CLASS_NAMESPACE

_activity = autoclass(ACTIVITY_CLASS_NAME).mActivity

_callbacks = {
    'on_new_intent': [],
    'on_activity_result': [],
}


class NewIntentListener(PythonJavaClass):
    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + '$NewIntentListener']
    __javacontext__ = 'app'

    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback

    @java_method('(Landroid/content/Intent;)V')
    def onNewIntent(self, intent):
        self.callback(intent)


class ActivityResultListener(PythonJavaClass):
    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + '$ActivityResultListener']
    __javacontext__ = 'app'

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(IILandroid/content/Intent;)V')
    def onActivityResult(self, requestCode, resultCode, intent):
        self.callback(requestCode, resultCode, intent)


def bind(**kwargs):
    for event, callback in kwargs.items():
        if event not in _callbacks:
            raise Exception('Unknown {!r} event'.format(event))
        elif event == 'on_new_intent':
            listener = NewIntentListener(callback)
            _activity.registerNewIntentListener(listener)
            _callbacks[event].append(listener)
        elif event == 'on_activity_result':
            listener = ActivityResultListener(callback)
            _activity.registerActivityResultListener(listener)
            _callbacks[event].append(listener)


def unbind(**kwargs):
    for event, callback in kwargs.items():
        if event not in _callbacks:
            raise Exception('Unknown {!r} event'.format(event))
        else:
            for listener in _callbacks[event][:]:
                if listener.callback == callback:
                    _callbacks[event].remove(listener)
                    if event == 'on_new_intent':
                        _activity.unregisterNewIntentListener(listener)
                    elif event == 'on_activity_result':
                        _activity.unregisterActivityResultListener(listener)


# Keep a reference to all the registered classes so that python doesn't
# garbage collect them.
_lifecycle_callbacks = set()


class ActivityLifecycleCallbacks(PythonJavaClass):
    """Callback class for handling PythonActivity lifecycle transitions"""

    __javainterfaces__ = ['android/app/Application$ActivityLifecycleCallbacks']

    def __init__(self, callbacks):
        super().__init__()

        # It would be nice to use keyword arguments, but PythonJavaClass
        # doesn't allow that in its __cinit__ method.
        if not isinstance(callbacks, dict):
            raise ValueError('callbacks must be a dict instance')
        self.callbacks = callbacks

    def _callback(self, name, *args):
        func = self.callbacks.get(name)
        if func:
            return func(*args)

    @java_method('(Landroid/app/Activity;Landroid/os/Bundle;)V')
    def onActivityCreated(self, activity, savedInstanceState):
        self._callback('onActivityCreated', activity, savedInstanceState)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityDestroyed(self, activity):
        self._callback('onActivityDestroyed', activity)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityPaused(self, activity):
        self._callback('onActivityPaused', activity)

    @java_method('(Landroid/app/Activity;Landroid/os/Bundle;)V')
    def onActivityPostCreated(self, activity, savedInstanceState):
        self._callback('onActivityPostCreated', activity, savedInstanceState)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityPostDestroyed(self, activity):
        self._callback('onActivityPostDestroyed', activity)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityPostPaused(self, activity):
        self._callback('onActivityPostPaused', activity)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityPostResumed(self, activity):
        self._callback('onActivityPostResumed', activity)

    @java_method('(Landroid/app/Activity;Landroid/os/Bundle;)V')
    def onActivityPostSaveInstanceState(self, activity, outState):
        self._callback('onActivityPostSaveInstanceState', activity, outState)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityPostStarted(self, activity):
        self._callback('onActivityPostStarted', activity)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityPostStopped(self, activity):
        self._callback('onActivityPostStopped', activity)

    @java_method('(Landroid/app/Activity;Landroid/os/Bundle;)V')
    def onActivityPreCreated(self, activity, savedInstanceState):
        self._callback('onActivityPreCreated', activity, savedInstanceState)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityPreDestroyed(self, activity):
        self._callback('onActivityPreDestroyed', activity)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityPrePaused(self, activity):
        self._callback('onActivityPrePaused', activity)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityPreResumed(self, activity):
        self._callback('onActivityPreResumed', activity)

    @java_method('(Landroid/app/Activity;Landroid/os/Bundle;)V')
    def onActivityPreSaveInstanceState(self, activity, outState):
        self._callback('onActivityPreSaveInstanceState', activity, outState)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityPreStarted(self, activity):
        self._callback('onActivityPreStarted', activity)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityPreStopped(self, activity):
        self._callback('onActivityPreStopped', activity)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityResumed(self, activity):
        self._callback('onActivityResumed', activity)

    @java_method('(Landroid/app/Activity;Landroid/os/Bundle;)V')
    def onActivitySaveInstanceState(self, activity, outState):
        self._callback('onActivitySaveInstanceState', activity, outState)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityStarted(self, activity):
        self._callback('onActivityStarted', activity)

    @java_method('(Landroid/app/Activity;)V')
    def onActivityStopped(self, activity):
        self._callback('onActivityStopped', activity)


def register_activity_lifecycle_callbacks(**callbacks):
    """Register ActivityLifecycleCallbacks instance

    The callbacks are supplied as keyword arguments corresponding to the
    Application.ActivityLifecycleCallbacks methods such as
    onActivityStarted. See the ActivityLifecycleCallbacks documentation
    for the signature of each method.

    The ActivityLifecycleCallbacks instance is returned so it can be
    supplied to unregister_activity_lifecycle_callbacks if needed.
    """
    instance = ActivityLifecycleCallbacks(callbacks)
    _lifecycle_callbacks.add(instance)

    # Use the registerActivityLifecycleCallbacks method from the
    # Activity class if it's available (API 29) since it guarantees the
    # callbacks will only be run for that activity. Otherwise, fallback
    # to the method on the Application class (API 14). In practice there
    # should be no difference since p4a applications only have a single
    # activity.
    if hasattr(_activity, 'registerActivityLifecycleCallbacks'):
        _activity.registerActivityLifecycleCallbacks(instance)
    else:
        app = _activity.getApplication()
        app.registerActivityLifecycleCallbacks(instance)
    return instance


def unregister_activity_lifecycle_callbacks(instance):
    """Unregister ActivityLifecycleCallbacks instance"""
    if hasattr(_activity, 'unregisterActivityLifecycleCallbacks'):
        _activity.unregisterActivityLifecycleCallbacks(instance)
    else:
        app = _activity.getApplication()
        app.unregisterActivityLifecycleCallbacks(instance)

    try:
        _lifecycle_callbacks.remove(instance)
    except KeyError:
        pass
