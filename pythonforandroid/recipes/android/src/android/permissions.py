import threading

try:
    from jnius import autoclass, PythonJavaClass, java_method
except ImportError:
    # To allow importing by build/manifest-creating code without
    # pyjnius being present:
    def autoclass(item):
        raise RuntimeError("pyjnius not available")


from android.config import ACTIVITY_CLASS_NAME, ACTIVITY_CLASS_NAMESPACE


class Permission:
    ACCEPT_HANDOVER = "android.permission.ACCEPT_HANDOVER"
    ACCESS_BACKGROUND_LOCATION = "android.permission.ACCESS_BACKGROUND_LOCATION"
    ACCESS_COARSE_LOCATION = "android.permission.ACCESS_COARSE_LOCATION"
    ACCESS_FINE_LOCATION = "android.permission.ACCESS_FINE_LOCATION"
    ACCESS_LOCATION_EXTRA_COMMANDS = (
        "android.permission.ACCESS_LOCATION_EXTRA_COMMANDS"
        )
    ACCESS_NETWORK_STATE = "android.permission.ACCESS_NETWORK_STATE"
    ACCESS_NOTIFICATION_POLICY = (
        "android.permission.ACCESS_NOTIFICATION_POLICY"
        )
    ACCESS_WIFI_STATE = "android.permission.ACCESS_WIFI_STATE"
    ADD_VOICEMAIL = "com.android.voicemail.permission.ADD_VOICEMAIL"
    ANSWER_PHONE_CALLS = "android.permission.ANSWER_PHONE_CALLS"
    BATTERY_STATS = "android.permission.BATTERY_STATS"
    BIND_ACCESSIBILITY_SERVICE = (
        "android.permission.BIND_ACCESSIBILITY_SERVICE"
        )
    BIND_AUTOFILL_SERVICE = "android.permission.BIND_AUTOFILL_SERVICE"
    BIND_CARRIER_MESSAGING_SERVICE = (  # note: deprecated in api 23+
        "android.permission.BIND_CARRIER_MESSAGING_SERVICE"
        )
    BIND_CARRIER_SERVICES = (  # replaces BIND_CARRIER_MESSAGING_SERVICE
        "android.permission.BIND_CARRIER_SERVICES"
        )
    BIND_CHOOSER_TARGET_SERVICE = (
        "android.permission.BIND_CHOOSER_TARGET_SERVICE"
        )
    BIND_CONDITION_PROVIDER_SERVICE = (
        "android.permission.BIND_CONDITION_PROVIDER_SERVICE"
        )
    BIND_DEVICE_ADMIN = "android.permission.BIND_DEVICE_ADMIN"
    BIND_DREAM_SERVICE = "android.permission.BIND_DREAM_SERVICE"
    BIND_INCALL_SERVICE = "android.permission.BIND_INCALL_SERVICE"
    BIND_INPUT_METHOD = (
        "android.permission.BIND_INPUT_METHOD"
        )
    BIND_MIDI_DEVICE_SERVICE = (
        "android.permission.BIND_MIDI_DEVICE_SERVICE"
        )
    BIND_NFC_SERVICE = (
        "android.permission.BIND_NFC_SERVICE"
        )
    BIND_NOTIFICATION_LISTENER_SERVICE = (
        "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE"
        )
    BIND_PRINT_SERVICE = (
        "android.permission.BIND_PRINT_SERVICE"
        )
    BIND_QUICK_SETTINGS_TILE = (
        "android.permission.BIND_QUICK_SETTINGS_TILE"
        )
    BIND_REMOTEVIEWS = (
        "android.permission.BIND_REMOTEVIEWS"
        )
    BIND_SCREENING_SERVICE = (
        "android.permission.BIND_SCREENING_SERVICE"
        )
    BIND_TELECOM_CONNECTION_SERVICE = (
        "android.permission.BIND_TELECOM_CONNECTION_SERVICE"
        )
    BIND_TEXT_SERVICE = (
        "android.permission.BIND_TEXT_SERVICE"
        )
    BIND_TV_INPUT = (
        "android.permission.BIND_TV_INPUT"
        )
    BIND_VISUAL_VOICEMAIL_SERVICE = (
        "android.permission.BIND_VISUAL_VOICEMAIL_SERVICE"
        )
    BIND_VOICE_INTERACTION = (
        "android.permission.BIND_VOICE_INTERACTION"
        )
    BIND_VPN_SERVICE = (
        "android.permission.BIND_VPN_SERVICE"
        )
    BIND_VR_LISTENER_SERVICE = (
        "android.permission.BIND_VR_LISTENER_SERVICE"
        )
    BIND_WALLPAPER = (
        "android.permission.BIND_WALLPAPER"
        )
    BLUETOOTH = (
        "android.permission.BLUETOOTH"
        )
    BLUETOOTH_ADMIN = (
        "android.permission.BLUETOOTH_ADMIN"
        )
    BODY_SENSORS = (
        "android.permission.BODY_SENSORS"
        )
    BROADCAST_PACKAGE_REMOVED = (
        "android.permission.BROADCAST_PACKAGE_REMOVED"
        )
    BROADCAST_STICKY = (
        "android.permission.BROADCAST_STICKY"
        )
    CALL_PHONE = (
        "android.permission.CALL_PHONE"
        )
    CALL_PRIVILEGED = (
        "android.permission.CALL_PRIVILEGED"
        )
    CAMERA = (
        "android.permission.CAMERA"
        )
    CAPTURE_AUDIO_OUTPUT = (
        "android.permission.CAPTURE_AUDIO_OUTPUT"
        )
    CAPTURE_SECURE_VIDEO_OUTPUT = (
        "android.permission.CAPTURE_SECURE_VIDEO_OUTPUT"
        )
    CAPTURE_VIDEO_OUTPUT = (
        "android.permission.CAPTURE_VIDEO_OUTPUT"
        )
    CHANGE_COMPONENT_ENABLED_STATE = (
        "android.permission.CHANGE_COMPONENT_ENABLED_STATE"
        )
    CHANGE_CONFIGURATION = (
        "android.permission.CHANGE_CONFIGURATION"
        )
    CHANGE_NETWORK_STATE = (
        "android.permission.CHANGE_NETWORK_STATE"
        )
    CHANGE_WIFI_MULTICAST_STATE = (
        "android.permission.CHANGE_WIFI_MULTICAST_STATE"
        )
    CHANGE_WIFI_STATE = (
        "android.permission.CHANGE_WIFI_STATE"
        )
    CLEAR_APP_CACHE = (
        "android.permission.CLEAR_APP_CACHE"
        )
    CONTROL_LOCATION_UPDATES = (
        "android.permission.CONTROL_LOCATION_UPDATES"
        )
    DELETE_CACHE_FILES = (
        "android.permission.DELETE_CACHE_FILES"
        )
    DELETE_PACKAGES = (
        "android.permission.DELETE_PACKAGES"
        )
    DIAGNOSTIC = (
        "android.permission.DIAGNOSTIC"
        )
    DISABLE_KEYGUARD = (
        "android.permission.DISABLE_KEYGUARD"
        )
    DUMP = (
        "android.permission.DUMP"
        )
    EXPAND_STATUS_BAR = (
        "android.permission.EXPAND_STATUS_BAR"
        )
    FACTORY_TEST = (
        "android.permission.FACTORY_TEST"
        )
    FOREGROUND_SERVICE = (
        "android.permission.FOREGROUND_SERVICE"
        )
    GET_ACCOUNTS = (
        "android.permission.GET_ACCOUNTS"
        )
    GET_ACCOUNTS_PRIVILEGED = (
        "android.permission.GET_ACCOUNTS_PRIVILEGED"
        )
    GET_PACKAGE_SIZE = (
        "android.permission.GET_PACKAGE_SIZE"
        )
    GET_TASKS = (
        "android.permission.GET_TASKS"
        )
    GLOBAL_SEARCH = (
        "android.permission.GLOBAL_SEARCH"
        )
    INSTALL_LOCATION_PROVIDER = (
        "android.permission.INSTALL_LOCATION_PROVIDER"
        )
    INSTALL_PACKAGES = (
        "android.permission.INSTALL_PACKAGES"
        )
    INSTALL_SHORTCUT = (
        "com.android.launcher.permission.INSTALL_SHORTCUT"
        )
    INSTANT_APP_FOREGROUND_SERVICE = (
        "android.permission.INSTANT_APP_FOREGROUND_SERVICE"
        )
    INTERNET = (
        "android.permission.INTERNET"
        )
    KILL_BACKGROUND_PROCESSES = (
        "android.permission.KILL_BACKGROUND_PROCESSES"
        )
    LOCATION_HARDWARE = (
        "android.permission.LOCATION_HARDWARE"
        )
    MANAGE_DOCUMENTS = (
        "android.permission.MANAGE_DOCUMENTS"
        )
    MANAGE_OWN_CALLS = (
        "android.permission.MANAGE_OWN_CALLS"
        )
    MASTER_CLEAR = (
        "android.permission.MASTER_CLEAR"
        )
    MEDIA_CONTENT_CONTROL = (
        "android.permission.MEDIA_CONTENT_CONTROL"
        )
    MODIFY_AUDIO_SETTINGS = (
        "android.permission.MODIFY_AUDIO_SETTINGS"
        )
    MODIFY_PHONE_STATE = (
        "android.permission.MODIFY_PHONE_STATE"
        )
    MOUNT_FORMAT_FILESYSTEMS = (
        "android.permission.MOUNT_FORMAT_FILESYSTEMS"
        )
    MOUNT_UNMOUNT_FILESYSTEMS = (
        "android.permission.MOUNT_UNMOUNT_FILESYSTEMS"
        )
    NFC = (
        "android.permission.NFC"
        )
    NFC_TRANSACTION_EVENT = (
        "android.permission.NFC_TRANSACTION_EVENT"
        )
    PACKAGE_USAGE_STATS = (
        "android.permission.PACKAGE_USAGE_STATS"
        )
    PERSISTENT_ACTIVITY = (
        "android.permission.PERSISTENT_ACTIVITY"
        )
    PROCESS_OUTGOING_CALLS = (
        "android.permission.PROCESS_OUTGOING_CALLS"
        )
    READ_CALENDAR = (
        "android.permission.READ_CALENDAR"
        )
    READ_CALL_LOG = (
        "android.permission.READ_CALL_LOG"
        )
    READ_CONTACTS = (
        "android.permission.READ_CONTACTS"
        )
    READ_EXTERNAL_STORAGE = (
        "android.permission.READ_EXTERNAL_STORAGE"
        )
    READ_FRAME_BUFFER = (
        "android.permission.READ_FRAME_BUFFER"
        )
    READ_INPUT_STATE = (
        "android.permission.READ_INPUT_STATE"
        )
    READ_LOGS = (
        "android.permission.READ_LOGS"
        )
    READ_PHONE_NUMBERS = (
        "android.permission.READ_PHONE_NUMBERS"
        )
    READ_PHONE_STATE = (
        "android.permission.READ_PHONE_STATE"
        )
    READ_SMS = (
        "android.permission.READ_SMS"
        )
    READ_SYNC_SETTINGS = (
        "android.permission.READ_SYNC_SETTINGS"
        )
    READ_SYNC_STATS = (
        "android.permission.READ_SYNC_STATS"
        )
    READ_VOICEMAIL = (
        "com.android.voicemail.permission.READ_VOICEMAIL"
        )
    REBOOT = (
        "android.permission.REBOOT"
        )
    RECEIVE_BOOT_COMPLETED = (
        "android.permission.RECEIVE_BOOT_COMPLETED"
        )
    RECEIVE_MMS = (
        "android.permission.RECEIVE_MMS"
        )
    RECEIVE_SMS = (
        "android.permission.RECEIVE_SMS"
        )
    RECEIVE_WAP_PUSH = (
        "android.permission.RECEIVE_WAP_PUSH"
        )
    RECORD_AUDIO = (
        "android.permission.RECORD_AUDIO"
        )
    REORDER_TASKS = (
        "android.permission.REORDER_TASKS"
        )
    REQUEST_COMPANION_RUN_IN_BACKGROUND = (
        "android.permission.REQUEST_COMPANION_RUN_IN_BACKGROUND"
        )
    REQUEST_COMPANION_USE_DATA_IN_BACKGROUND = (
        "android.permission.REQUEST_COMPANION_USE_DATA_IN_BACKGROUND"
        )
    REQUEST_DELETE_PACKAGES = (
        "android.permission.REQUEST_DELETE_PACKAGES"
        )
    REQUEST_IGNORE_BATTERY_OPTIMIZATIONS = (
        "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS"
        )
    REQUEST_INSTALL_PACKAGES = (
        "android.permission.REQUEST_INSTALL_PACKAGES"
        )
    RESTART_PACKAGES = (
        "android.permission.RESTART_PACKAGES"
        )
    SEND_RESPOND_VIA_MESSAGE = (
        "android.permission.SEND_RESPOND_VIA_MESSAGE"
        )
    SEND_SMS = (
        "android.permission.SEND_SMS"
        )
    SET_ALARM = (
        "com.android.alarm.permission.SET_ALARM"
        )
    SET_ALWAYS_FINISH = (
        "android.permission.SET_ALWAYS_FINISH"
        )
    SET_ANIMATION_SCALE = (
        "android.permission.SET_ANIMATION_SCALE"
        )
    SET_DEBUG_APP = (
        "android.permission.SET_DEBUG_APP"
        )
    SET_PREFERRED_APPLICATIONS = (
        "android.permission.SET_PREFERRED_APPLICATIONS"
        )
    SET_PROCESS_LIMIT = (
        "android.permission.SET_PROCESS_LIMIT"
        )
    SET_TIME = (
        "android.permission.SET_TIME"
        )
    SET_TIME_ZONE = (
        "android.permission.SET_TIME_ZONE"
        )
    SET_WALLPAPER = (
        "android.permission.SET_WALLPAPER"
        )
    SET_WALLPAPER_HINTS = (
        "android.permission.SET_WALLPAPER_HINTS"
        )
    SIGNAL_PERSISTENT_PROCESSES = (
        "android.permission.SIGNAL_PERSISTENT_PROCESSES"
        )
    STATUS_BAR = (
        "android.permission.STATUS_BAR"
        )
    SYSTEM_ALERT_WINDOW = (
        "android.permission.SYSTEM_ALERT_WINDOW"
        )
    TRANSMIT_IR = (
        "android.permission.TRANSMIT_IR"
        )
    UNINSTALL_SHORTCUT = (
        "com.android.launcher.permission.UNINSTALL_SHORTCUT"
        )
    UPDATE_DEVICE_STATS = (
        "android.permission.UPDATE_DEVICE_STATS"
        )
    USE_BIOMETRIC = (
        "android.permission.USE_BIOMETRIC"
        )
    USE_FINGERPRINT = (
        "android.permission.USE_FINGERPRINT"
        )
    USE_SIP = (
        "android.permission.USE_SIP"
        )
    VIBRATE = (
        "android.permission.VIBRATE"
        )
    WAKE_LOCK = (
        "android.permission.WAKE_LOCK"
        )
    WRITE_APN_SETTINGS = (
        "android.permission.WRITE_APN_SETTINGS"
        )
    WRITE_CALENDAR = (
        "android.permission.WRITE_CALENDAR"
        )
    WRITE_CALL_LOG = (
        "android.permission.WRITE_CALL_LOG"
        )
    WRITE_CONTACTS = (
        "android.permission.WRITE_CONTACTS"
        )
    WRITE_EXTERNAL_STORAGE = (
        "android.permission.WRITE_EXTERNAL_STORAGE"
        )
    WRITE_GSERVICES = (
        "android.permission.WRITE_GSERVICES"
        )
    WRITE_SECURE_SETTINGS = (
        "android.permission.WRITE_SECURE_SETTINGS"
        )
    WRITE_SETTINGS = (
        "android.permission.WRITE_SETTINGS"
        )
    WRITE_SYNC_SETTINGS = (
        "android.permission.WRITE_SYNC_SETTINGS"
        )
    WRITE_VOICEMAIL = (
        "com.android.voicemail.permission.WRITE_VOICEMAIL"
        )


PERMISSION_GRANTED = 0
PERMISSION_DENIED = -1


class _onRequestPermissionsCallback(PythonJavaClass):
    """Callback class for registering a Python callback from
    onRequestPermissionsResult in PythonActivity.
    """
    __javainterfaces__ = [ACTIVITY_CLASS_NAMESPACE + '$PermissionsCallback']
    __javacontext__ = 'app'

    def __init__(self, func):
        self.func = func
        super().__init__()

    @java_method('(I[Ljava/lang/String;[I)V')
    def onRequestPermissionsResult(self, requestCode,
                                   permissions, grantResults):
        self.func(requestCode, permissions, grantResults)


class _RequestPermissionsManager:
    """Internal class for requesting Android permissions.

    Permissions are requested through the method 'request_permissions' which
    accepts a list of permissions and an optional callback.

    Any callback will asynchronously receive arguments from
    onRequestPermissionsResult on PythonActivity after requestPermissions is
    called.

    The callback supplied must accept two arguments: 'permissions' and
    'grantResults' (as supplied to onPermissionsCallbackResult).

    Note that for SDK_INT < 23, run-time permissions are not required, and so
    the callback will be called immediately.

    The attribute '_java_callback' is initially None, but is set when the first
    permissions request is made. It is set to an instance of
    onRequestPermissionsCallback, which allows the Java callback to be
    propagated to the class method 'python_callback'. This is then, in turn,
    used to call an application callback if provided to request_permissions.

    The attribute '_callback_id' is incremented with each call to
    request_permissions which has a callback (the value '1' is used for any
    call which does not pass a callback). This is passed to requestCode in
    the Java call, and used to identify (via the _callbacks dictionary)
    the matching call.
    """
    _SDK_INT = None
    _java_callback = None
    _callbacks = {1: None}
    _callback_id = 1
    # Lock to prevent multiple calls to request_permissions being handled
    # simultaneously (as incrementing _callback_id is not atomic)
    _lock = threading.Lock()

    @classmethod
    def register_callback(cls):
        """Register Java callback for requestPermissions."""
        cls._java_callback = _onRequestPermissionsCallback(cls.python_callback)
        mActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
        mActivity.addPermissionsCallback(cls._java_callback)

    @classmethod
    def request_permissions(cls, permissions, callback=None):
        """Requests Android permissions from PythonActivity.
        If 'callback' is supplied, the request is made with a new requestCode
        and the callback is stored in the _callbacks dict. When a Java callback
        with the matching requestCode is received, callback will be called
        with arguments of 'permissions' and 'grant_results'.
        """
        if not cls._SDK_INT:
            # Get the Android build version and store it
            VERSION = autoclass('android.os.Build$VERSION')
            cls.SDK_INT = VERSION.SDK_INT
        if cls.SDK_INT < 23:
            # No run-time permissions needed, return immediately.
            if callback:
                callback(permissions, [True for x in permissions])
                return
        # Request permissions
        with cls._lock:
            if not cls._java_callback:
                cls.register_callback()
            mActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
            if not callback:
                mActivity.requestPermissions(permissions)
            else:
                cls._callback_id += 1
                mActivity.requestPermissionsWithRequestCode(
                    permissions, cls._callback_id)
                cls._callbacks[cls._callback_id] = callback

    @classmethod
    def python_callback(cls, requestCode, permissions, grantResults):
        """Calls the relevant callback with arguments of 'permissions'
        and 'grantResults'."""
        # Convert from Android codes to True/False
        grant_results = [x == PERMISSION_GRANTED for x in grantResults]
        if cls._callbacks.get(requestCode):
            cls._callbacks[requestCode](permissions, grant_results)


# Public API methods for requesting permissions

def request_permissions(permissions, callback=None):
    """Requests Android permissions.

    Args:
        permissions (str): A list of permissions to requests (str)
        callback (callable, optional): A function to call when the request
            is completed (callable)

    Returns:
        None

    Notes:

    Permission strings can be imported from the 'Permission' class in this
    module. For example:

    from android import Permission
        permissions_list = [Permission.CAMERA,
                            Permission.WRITE_EXTERNAL_STORAGE]

    See the p4a source file 'permissions.py' for a list of valid permission
    strings (pythonforandroid/recipes/android/src/android/permissions.py).

    Any callback supplied must accept two arguments:
       permissions (list of str): A list of permission strings
       grant_results (list of bool): A list of bools indicating whether the
           respective permission was granted.
    See Android documentation for onPermissionsCallbackResult for
    further information.

    Note that if the request is interupted the callback may contain an empty
    list of permissions, without permissions being granted; the App should
    check that each permission requested has been granted.

    Also note that when calling request_permission on SDK_INT < 23, the
    callback will be returned immediately as requesting permissions is not
    required.
    """
    _RequestPermissionsManager.request_permissions(permissions, callback)


def request_permission(permission, callback=None):
    request_permissions([permission], callback)


def check_permission(permission):
    """Checks if an app holds the passed permission.

    Args:
        - permission     An Android permission (str)

    Returns:
        bool: True if the app holds the permission given, False otherwise.
    """
    mActivity = autoclass(ACTIVITY_CLASS_NAME).mActivity
    result = bool(mActivity.checkCurrentPermission(
        permission + ""
    ))
    return result
