from jnius import autoclass, cast
import os

from android.config import ACTIVITY_CLASS_NAME, SERVICE_CLASS_NAME


Environment = autoclass('android.os.Environment')
File = autoclass('java.io.File')


def _android_has_is_removable_func():
    VERSION = autoclass('android.os.Build$VERSION')
    return (VERSION.SDK_INT >= 24)


def _get_sdcard_path():
    """ Internal function to return getExternalStorageDirectory()
        path. This is internal because it may either return the internal,
        or an external sd card, depending on the device.
        Use primary_external_storage_path()
        or secondary_external_storage_path() instead which try to
        distinguish this properly.
    """
    return (
        Environment.getExternalStorageDirectory().getAbsolutePath()
    )


def _get_activity():
    """
    Retrieves the activity from `PythonActivity` fallback to `PythonService`.
    """
    PythonActivity = autoclass(ACTIVITY_CLASS_NAME)
    activity = PythonActivity.mActivity
    if activity is None:
        # assume we're running from the background service
        PythonService = autoclass(SERVICE_CLASS_NAME)
        activity = PythonService.mService
    return activity


def app_storage_path():
    """ Locate the built-in device storage used for this app only.

        This storage is APP-SPECIFIC, and not visible to other apps.
        It will be wiped when your app is uninstalled.

        Returns directory path to storage.
    """
    activity = _get_activity()
    currentActivity = cast('android.app.Activity', activity)
    context = cast('android.content.ContextWrapper',
                   currentActivity.getApplicationContext())
    file_p = cast('java.io.File', context.getFilesDir())
    return os.path.normpath(os.path.abspath(
        file_p.getAbsolutePath().replace("/", os.path.sep)))


def primary_external_storage_path():
    """ Locate the built-in device storage that user can see via file browser.
        Often found at: /sdcard/

        This is storage is SHARED, and visible to other apps and the user.
        It will remain untouched when your app is uninstalled.

        Returns directory path to storage.

        WARNING: You need storage permissions to access this storage.
    """
    if _android_has_is_removable_func():
        sdpath = _get_sdcard_path()
        # Apparently this can both return primary (built-in) or
        # secondary (removable) external storage depending on the device,
        # therefore check that we got what we wanted:
        if not Environment.isExternalStorageRemovable(File(sdpath)):
            return sdpath
    if "EXTERNAL_STORAGE" in os.environ:
        return os.environ["EXTERNAL_STORAGE"]
    raise RuntimeError(
        "unexpectedly failed to determine " +
        "primary external storage path"
    )


def secondary_external_storage_path():
    """ Locate the external SD Card storage, which may not be present.
        Often found at: /sdcard/External_SD/

        This storage is SHARED, visible to other apps, and may not be
        be available if the user didn't put in an external SD card.
        It will remain untouched when your app is uninstalled.

        Returns None if not found, otherwise path to storage.

        WARNING: You need storage permissions to access this storage.
                 If it is not writable and presents as empty even with
                 permissions, then the external sd card may not be present.
    """
    if _android_has_is_removable_func:
        # See if getExternalStorageDirectory() returns secondary ext storage:
        sdpath = _get_sdcard_path()
        # Apparently this can both return primary (built-in) or
        # secondary (removable) external storage depending on the device,
        # therefore check that we got what we wanted:
        if Environment.isExternalStorageRemovable(File(sdpath)):
            if os.path.exists(sdpath):
                return sdpath

    # See if we can take a guess based on environment variables:
    p = None
    if "SECONDARY_STORAGE" in os.environ:
        p = os.environ["SECONDARY_STORAGE"]
    elif "EXTERNAL_SDCARD_STORAGE" in os.environ:
        p = os.environ["EXTERNAL_SDCARD_STORAGE"]
    if p is not None and os.path.exists(p):
        return p
    return None
