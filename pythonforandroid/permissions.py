"""
.. _perm_groups:

Permission groups for Android
=============================

A collection of permissions fetched directly from the Android source code,
grouped by the categories presented in the ``AndroidManifest.xml``

Permission names and permission groups are licensed under Apache 2.0 License,
Copyright 2006, The Android Open Source Project

* CONTACTS - Permissions for accessing user's contacts including personal
  profile

* CALENDAR - Permissions for accessing user's calendar

* SMS - Permissions for accessing and modifying user's SMS messages

* STORAGE - Permissions for accessing external storage

* LOCATION - Permissions for accessing the device location

* PHONE - Permissions for accessing the device telephony

* MICROPHONE - Permissions for accessing the device microphone

* UCE - Permissions for accessing the UCE Service

* CAMERA - Permissions for accessing the device camera

* SENSORS - Permissions for accessing the device sensors

* REMOVED - Permissions removed in the latest source kept for backwards
  compatibility

* ALARM - Permissions for setting the device alarm

* VOICEMAIL  - Permissions for accessing the user voicemail

* LOCATION - Permissions for accessing location info

* NETWORKS - Permissions for accessing Internet, WiFi and short range,
  peripheral networks

* ACCOUNTS - Permissions for accessing accounts

* HARDWARE - Permissions for accessing hardware that may effect battery life

* AUDIO - Permissions related to changing audio settings

* SCREENLOCK - Permissions for screenlock

* ACCESS_APPS - Permissions to access other installed applications

* DISPLAY_AFFECT - Permissions affecting the display of other applications

* CLOCK - Permissions for changing the system clock

* STATUSBAR - Permissions related to changing status bar

* SHORTCUT - Permissions related to adding/removing shortcuts from Launcher
  (applications drawer)

* SYNC - Permissions related to accessing sync settings

* LOW_LEVEL - Permissions for low-level system interaction

.. warning::

   **Do not use** the permission groups below this line in production! If you
   really need such permissions, ensure you use only **some** of them.

* INSTALL - Permissions for accessing messages between apps, premium
  shortcodes, etc.
* DEVELOPMENT - Permissions for special development tools
* PRIVATE - Private (system) permissions
* __ALL_PERMISSIONS__ -
"""

# Permissions for accessing user's contacts including personal profile
CONTACTS = [
    'READ_CONTACTS',
    'WRITE_CONTACTS',
]

# Permissions for accessing user's calendar
CALENDAR = [
    'READ_CALENDAR',
    'WRITE_CALENDAR',
]

# Permissions for accessing and modifying user's SMS messages
SMS = [
    'SEND_SMS',
    'RECEIVE_SMS',
    'READ_SMS',
    'RECEIVE_WAP_PUSH',
    'RECEIVE_MMS',
    'READ_CELL_BROADCASTS',
]

# Permissions for accessing external storage
STORAGE = [
    'READ_EXTERNAL_STORAGE',
    'WRITE_EXTERNAL_STORAGE',
    'WRITE_MEDIA_STORAGE',
    'MANAGE_DOCUMENTS',
    'CACHE_CONTENT',
]

# Permissions for accessing the device location
LOCATION = [
    'ACCESS_FINE_LOCATION',
    'ACCESS_COARSE_LOCATION',
]

# Permissions for accessing the device telephony
PHONE = [
    'READ_PHONE_STATE',
    'CALL_PHONE',
    'ACCESS_IMS_CALL_SERVICE',
    'READ_CALL_LOG',
    'WRITE_CALL_LOG',
    'com.android.voicemail.permission.ADD_VOICEMAIL',
    'USE_SIP',
    'PROCESS_OUTGOING_CALLS',
    'MODIFY_PHONE_STATE',
    'READ_PRECISE_PHONE_STATE',
    'READ_PRIVILEGED_PHONE_STATE',
    'REGISTER_SIM_SUBSCRIPTION',
    'REGISTER_CALL_PROVIDER',
    'REGISTER_CONNECTION_MANAGER',
    'BIND_INCALL_SERVICE',
    'BIND_SCREENING_SERVICE',
    'BIND_CONNECTION_SERVICE',
    'BIND_TELECOM_CONNECTION_SERVICE',
    'CONTROL_INCALL_EXPERIENCE',
    'RECEIVE_STK_COMMANDS',
]

# Permissions for accessing the device microphone
MICROPHONE = [
    'RECORD_AUDIO',
]

# Permissions for accessing the UCE Service
UCE = [
    'ACCESS_UCE_PRESENCE_SERVICE',
    'ACCESS_UCE_OPTIONS_SERVICE',
]

# Permissions for accessing the device camera
CAMERA = [
    'CAMERA',
    'CAMERA_DISABLE_TRANSMIT_LED',
    'CAMERA_SEND_SYSTEM_EVENTS',
]

# Permissions for accessing the device sensors
SENSORS = [
    'BODY_SENSORS',
    'USE_FINGERPRINT',
]

REMOVED = [
    'READ_PROFILE',
    'WRITE_PROFILE',
    'READ_SOCIAL_STREAM',
    'WRITE_SOCIAL_STREAM',
    'READ_USER_DICTIONARY',
    'WRITE_USER_DICTIONARY',
    'WRITE_SMS',
    'com.android.browser.permission.READ_HISTORY_BOOKMARKS',
    'com.android.browser.permission.WRITE_HISTORY_BOOKMARKS',
    'AUTHENTICATE_ACCOUNTS',
    'MANAGE_ACCOUNTS',
    'USE_CREDENTIALS',
    'SUBSCRIBED_FEEDS_READ',
    'SUBSCRIBED_FEEDS_WRITE',
    'FLASHLIGHT',
]

INSTALL = [
    'SEND_RESPOND_VIA_MESSAGE',
    'SEND_SMS_NO_CONFIRMATION',
    'CARRIER_FILTER_SMS',
    'RECEIVE_EMERGENCY_BROADCAST',
    'RECEIVE_BLUETOOTH_MAP',
    'BIND_DIRECTORY_SEARCH',
    'MODIFY_CELL_BROADCASTS',
]

# Permissions for setting the device alarm
ALARM = [
    'com.android.alarm.permission.SET_ALARM',
]

# Permissions for accessing the user voicemail
VOICEMAIL = [
    'com.android.voicemail.permission.WRITE_VOICEMAIL',
    'com.android.voicemail.permission.READ_VOICEMAIL',
]

# Permissions for accessing location info
LOCATION = [
    'ACCESS_LOCATION_EXTRA_COMMANDS',
    'INSTALL_LOCATION_PROVIDER',
    'HDMI_CEC',
    'LOCATION_HARDWARE',
    'ACCESS_MOCK_LOCATION',
]

# Permissions for accessing networks
# Permissions for short range, peripheral networks
NETWORKS = [
    'INTERNET',
    'ACCESS_NETWORK_STATE',
    'ACCESS_WIFI_STATE',
    'CHANGE_WIFI_STATE',
    'READ_WIFI_CREDENTIAL',
    'TETHER_PRIVILEGED',
    'RECEIVE_WIFI_CREDENTIAL_CHANGE',
    'OVERRIDE_WIFI_CONFIG',
    'ACCESS_WIMAX_STATE',
    'CHANGE_WIMAX_STATE',
    'SCORE_NETWORKS',
    'BLUETOOTH',
    'BLUETOOTH_ADMIN',
    'BLUETOOTH_PRIVILEGED',
    'BLUETOOTH_MAP',
    'BLUETOOTH_STACK',
    'NFC',
    'CONNECTIVITY_INTERNAL',
    'CONNECTIVITY_USE_RESTRICTED_NETWORKS',
    'PACKET_KEEPALIVE_OFFLOAD',
    'RECEIVE_DATA_ACTIVITY_CHANGE',
    'LOOP_RADIO',
    'NFC_HANDOVER_STATUS',
]

# Permissions for accessing accounts
ACCOUNTS = [
    'GET_ACCOUNTS',
    'ACCOUNT_MANAGER',
]

# Permissions for accessing hardware that may effect battery life
HARDWARE = [
    'CHANGE_WIFI_MULTICAST_STATE',
    'VIBRATE',
    'WAKE_LOCK',
    'TRANSMIT_IR',
    'MANAGE_USB',
    'ACCESS_MTP',
    'HARDWARE_TEST',
    'ACCESS_FM_RADIO',
    'NET_ADMIN',
    'REMOTE_AUDIO_PLAYBACK',
    'TV_INPUT_HARDWARE',
    'CAPTURE_TV_INPUT',
    'DVB_DEVICE',
    'READ_OEM_UNLOCK_STATE',
    'OEM_UNLOCK_STATE',
    'ACCESS_PDB_STATE',
    'NOTIFY_PENDING_SYSTEM_UPDATE',
]

AUDIO = [
    'MODIFY_AUDIO_SETTINGS',
]

# Permissions for screenlock
SCREENLOCK = [
    'DISABLE_KEYGUARD',
]

ACCESS_APPS = [
    'GET_TASKS',
    'REAL_GET_TASKS',
    'START_TASKS_FROM_RECENTS',
    'INTERACT_ACROSS_USERS',
    'INTERACT_ACROSS_USERS_FULL',
    'MANAGE_USERS',
    'CREATE_USERS',
    'MANAGE_PROFILE_AND_DEVICE_OWNERS',
    'GET_DETAILED_TASKS',
    'REORDER_TASKS',
    'REMOVE_TASKS',
    'MANAGE_ACTIVITY_STACKS',
    'START_ANY_ACTIVITY',
    'RESTART_PACKAGES',
    'KILL_BACKGROUND_PROCESSES',
    'GET_PROCESS_STATE_AND_OOM_SCORE',
    'GET_PACKAGE_IMPORTANCE',
    'GET_INTENT_SENDER_INTENT',
]

DISPLAY_AFFECT = [
    'SYSTEM_ALERT_WINDOW',
    'SET_WALLPAPER',
    'SET_WALLPAPER_HINTS',
]

# Permissions for changing the system clock
CLOCK = [
    'SET_TIME',
    'SET_TIME_ZONE',
]

STATUSBAR = [
    'EXPAND_STATUS_BAR',
]

SHORTCUT = [
    'com.android.launcher.permission.INSTALL_SHORTCUT',
    'com.android.launcher.permission.UNINSTALL_SHORTCUT',
]

SYNC = [
    'READ_SYNC_SETTINGS',
    'WRITE_SYNC_SETTINGS',
    'READ_SYNC_STATS',
]

# Permissions for low-level system interaction
LOW_LEVEL = [
    'SET_SCREEN_COMPATIBILITY',
    'CHANGE_CONFIGURATION',
    'WRITE_SETTINGS',
    'WRITE_GSERVICES',
    'FORCE_STOP_PACKAGES',
    'RETRIEVE_WINDOW_CONTENT',
    'SET_ANIMATION_SCALE',
    'PERSISTENT_ACTIVITY',
    'GET_PACKAGE_SIZE',
    'SET_PREFERRED_APPLICATIONS',
    'RECEIVE_BOOT_COMPLETED',
    'BROADCAST_STICKY',
    'MOUNT_UNMOUNT_FILESYSTEMS',
    'MOUNT_FORMAT_FILESYSTEMS',
    'STORAGE_INTERNAL',
    'ASEC_ACCESS',
    'ASEC_CREATE',
    'ASEC_DESTROY',
    'ASEC_MOUNT_UNMOUNT',
    'ASEC_RENAME',
    'WRITE_APN_SETTINGS',
    'CHANGE_NETWORK_STATE',
    'CLEAR_APP_CACHE',
    'ALLOW_ANY_CODEC_FOR_PLAYBACK',
    'MANAGE_CA_CERTIFICATES',
    'RECOVERY',
    'BIND_JOB_SERVICE',
    'RESET_SHORTCUT_MANAGER_THROTTLING',
    'UPDATE_CONFIG',
]

# Permissions for special development tools
DEVELOPMENT = [
    'WRITE_SECURE_SETTINGS',
    'DUMP',
    'READ_LOGS',
    'SET_DEBUG_APP',
    'SET_PROCESS_LIMIT',
    'SET_ALWAYS_FINISH',
    'SIGNAL_PERSISTENT_PROCESSES',
]

PRIVATE = [
    'GET_ACCOUNTS_PRIVILEGED',
    'GET_PASSWORD',
    'DIAGNOSTIC',
    'STATUS_BAR',
    'STATUS_BAR_SERVICE',
    'BIND_QUICK_SETTINGS_TILE',
    'FORCE_BACK',
    'UPDATE_DEVICE_STATS',
    'GET_APP_OPS_STATS',
    'UPDATE_APP_OPS_STATS',
    'MANAGE_APP_OPS_RESTRICTIONS',
    'INTERNAL_SYSTEM_WINDOW',
    'MANAGE_APP_TOKENS',
    'REGISTER_WINDOW_MANAGER_LISTENERS',
    'FREEZE_SCREEN',
    'INJECT_EVENTS',
    'FILTER_EVENTS',
    'RETRIEVE_WINDOW_TOKEN',
    'FRAME_STATS',
    'TEMPORARY_ENABLE_ACCESSIBILITY',
    'SET_ACTIVITY_WATCHER',
    'SHUTDOWN',
    'STOP_APP_SWITCHES',
    'GET_TOP_ACTIVITY_INFO',
    'READ_INPUT_STATE',
    'BIND_INPUT_METHOD',
    'BIND_MIDI_DEVICE_SERVICE',
    'BIND_ACCESSIBILITY_SERVICE',
    'BIND_PRINT_SERVICE',
    'BIND_PRINT_RECOMMENDATION_SERVICE',
    'BIND_NFC_SERVICE',
    'BIND_PRINT_SPOOLER_SERVICE',
    'BIND_RUNTIME_PERMISSION_PRESENTER_SERVICE',
    'BIND_TEXT_SERVICE',
    'BIND_VPN_SERVICE',
    'BIND_WALLPAPER',
    'BIND_VOICE_INTERACTION',
    'MANAGE_VOICE_KEYPHRASES',
    'BIND_REMOTE_DISPLAY',
    'BIND_TV_INPUT',
    'BIND_TV_REMOTE_SERVICE',
    'TV_VIRTUAL_REMOTE_CONTROLLER',
    'MODIFY_PARENTAL_CONTROLS',
    'BIND_ROUTE_PROVIDER',
    'BIND_DEVICE_ADMIN',
    'MANAGE_DEVICE_ADMINS',
    'SET_ORIENTATION',
    'SET_POINTER_SPEED',
    'SET_INPUT_CALIBRATION',
    'SET_KEYBOARD_LAYOUT',
    'TABLET_MODE',
    'REQUEST_INSTALL_PACKAGES',
    'INSTALL_PACKAGES',
    'CLEAR_APP_USER_DATA',
    'GET_APP_GRANTED_URI_PERMISSIONS',
    'CLEAR_APP_GRANTED_URI_PERMISSIONS',
    'DELETE_CACHE_FILES',
    'DELETE_PACKAGES',
    'MOVE_PACKAGE',
    'CHANGE_COMPONENT_ENABLED_STATE',
    'GRANT_RUNTIME_PERMISSIONS',
    'INSTALL_GRANT_RUNTIME_PERMISSIONS',
    'REVOKE_RUNTIME_PERMISSIONS',
    'OBSERVE_GRANT_REVOKE_PERMISSIONS',
    'ACCESS_SURFACE_FLINGER',
    'READ_FRAME_BUFFER',
    'ACCESS_INPUT_FLINGER',
    'CONFIGURE_WIFI_DISPLAY',
    'CONTROL_WIFI_DISPLAY',
    'CONFIGURE_DISPLAY_COLOR_MODE',
    'CONTROL_VPN',
    'CONTROL_VPN',
    'CAPTURE_AUDIO_OUTPUT',
    'CAPTURE_AUDIO_HOTWORD',
    'MODIFY_AUDIO_ROUTING',
    'CAPTURE_VIDEO_OUTPUT',
    'CAPTURE_SECURE_VIDEO_OUTPUT',
    'MEDIA_CONTENT_CONTROL',
    'BRICK',
    'REBOOT',
    'DEVICE_POWER',
    'USER_ACTIVITY',
    'NET_TUNNELING',
    'FACTORY_TEST',
    'BROADCAST_PACKAGE_REMOVED',
    'BROADCAST_SMS',
    'BROADCAST_WAP_PUSH',
    'BROADCAST_NETWORK_PRIVILEGED',
    'MASTER_CLEAR',
    'CALL_PRIVILEGED',
    'PERFORM_CDMA_PROVISIONING',
    'PERFORM_SIM_ACTIVATION',
    'CONTROL_LOCATION_UPDATES',
    'ACCESS_CHECKIN_PROPERTIES',
    'PACKAGE_USAGE_STATS',
    'CHANGE_APP_IDLE_STATE',
    'CHANGE_DEVICE_IDLE_TEMP_WHITELIST',
    'REQUEST_IGNORE_BATTERY_OPTIMIZATIONS',
    'BATTERY_STATS',
    'BACKUP',
    'CONFIRM_FULL_BACKUP',
    'BIND_REMOTEVIEWS',
    'BIND_APPWIDGET',
    'BIND_KEYGUARD_APPWIDGET',
    'MODIFY_APPWIDGET_BIND_PERMISSIONS',
    'CHANGE_BACKGROUND_DATA_SETTING',
    'GLOBAL_SEARCH',
    'GLOBAL_SEARCH_CONTROL',
    'READ_SEARCH_INDEXABLES',
    'SET_WALLPAPER_COMPONENT',
    'READ_DREAM_STATE',
    'WRITE_DREAM_STATE',
    'ACCESS_CACHE_FILESYSTEM',
    'COPY_PROTECTED_DATA',
    'CRYPT_KEEPER',
    'READ_NETWORK_USAGE_HISTORY',
    'MANAGE_NETWORK_POLICY',
    'MODIFY_NETWORK_ACCOUNTING',
    'android.intent.category.MASTER_CLEAR.permission.C2D_MESSAGE',
    'PACKAGE_VERIFICATION_AGENT',
    'BIND_PACKAGE_VERIFIER',
    'INTENT_FILTER_VERIFICATION_AGENT',
    'BIND_INTENT_FILTER_VERIFIER',
    'SERIAL_PORT',
    'ACCESS_CONTENT_PROVIDERS_EXTERNALLY',
    'UPDATE_LOCK',
    'ACCESS_NOTIFICATIONS',
    'ACCESS_NOTIFICATION_POLICY',
    'MANAGE_NOTIFICATIONS',
    'ACCESS_KEYGUARD_SECURE_STORAGE',
    'MANAGE_FINGERPRINT',
    'RESET_FINGERPRINT_LOCKOUT',
    'CONTROL_KEYGUARD',
    'TRUST_LISTENER',
    'PROVIDE_TRUST_AGENT',
    'LAUNCH_TRUST_AGENT_SETTINGS',
    'BIND_TRUST_AGENT',
    'BIND_NOTIFICATION_LISTENER_SERVICE',
    'BIND_NOTIFICATION_RANKER_SERVICE',
    'BIND_CHOOSER_TARGET_SERVICE',
    'BIND_CONDITION_PROVIDER_SERVICE',
    'BIND_DREAM_SERVICE',
    'INVOKE_CARRIER_SETUP',
    'ACCESS_NETWORK_CONDITIONS',
    'ACCESS_DRM_CERTIFICATES',
    'MANAGE_MEDIA_PROJECTION',
    'READ_INSTALL_SESSIONS',
    'REMOVE_DRM_CERTIFICATES',
    'BIND_CARRIER_MESSAGING_SERVICE',
    'ACCESS_VOICE_INTERACTION_SERVICE',
    'BIND_CARRIER_SERVICES',
    'QUERY_DO_NOT_ASK_CREDENTIALS_ON_BOOT',
    'KILL_UID',
    'LOCAL_MAC_ADDRESS',
    'PEERS_MAC_ADDRESS',
    'DISPATCH_NFC_MESSAGE',
    'MODIFY_DAY_NIGHT_MODE',
    'ACCESS_EPHEMERAL_APPS',
    'RECEIVE_MEDIA_RESOURCE_USAGE',
    'MANAGE_SOUND_TRIGGER',
    'DISPATCH_PROVISIONING_MESSAGE',
    'READ_BLOCKED_NUMBERS',
    'WRITE_BLOCKED_NUMBERS',
    'BIND_VR_LISTENER_SERVICE',
    'ACCESS_VR_MANAGER',
    'UPDATE_LOCK_TASK_PACKAGES',
    'SUBSTITUTE_NOTIFICATION_APP_NAME',
]

__ALL_PERMISSIONS__ = (
    CONTACTS + CALENDAR + SMS + STORAGE + LOCATION +
    PHONE + MICROPHONE + UCE + CAMERA + SENSORS + REMOVED +
    ALARM + VOICEMAIL + LOCATION + NETWORKS + ACCOUNTS + HARDWARE +
    AUDIO + SCREENLOCK + ACCESS_APPS + DISPLAY_AFFECT + CLOCK +
    STATUSBAR + SHORTCUT + SYNC + LOW_LEVEL +
    INSTALL + DEVELOPMENT + PRIVATE)
