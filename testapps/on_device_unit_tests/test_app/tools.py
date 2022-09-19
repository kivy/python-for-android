# -*- coding: utf-8 -*-

import glob
import unittest

try:
    # python2 case
    from StringIO import StringIO
except ImportError:
    # python3 case
    from io import StringIO
from os.path import abspath, split, join

from constants import RUNNING_ON_ANDROID

APP_PATH = split(abspath(__file__))[0]


def run_test_suites_into_buffer(suites):
    """Run a suite of unittests but into a buffer so we can read the result."""
    terminal_output = StringIO()
    unittest.TextTestRunner(stream=terminal_output).run(suites)
    return terminal_output.getvalue()


def get_images_with_extension(path=APP_PATH, extension='*.png'):
    """
    Return a list of image files given a path and an file extension.

    .. note:: those image files are supposed to be created by our unittests
              inside the app's root folder.
    """
    return glob.glob(join(path, extension))


def load_kv_from(kv_name):
    """
    Load a kivy's kv file givel a kv filename.

    .. note:: requires `.kv` extension.
    """
    from kivy.lang import Builder

    kv_file = join(APP_PATH, kv_name)
    return Builder.load_file(kv_file)


def raise_error(error):
    """
    A function to notify an error without raising an exception.

    .. warning:: we will try to notify via an kivy's Popup, but if kivy is not
              installed, it will only print an error message.
    """
    try:
        from widgets import ErrorPopup
    except ImportError:
        print('raise_error:',  error)
        return
    ErrorPopup(error_text=error).open()


def get_failed_unittests_from(unittests_output, set_of_tests):
    """Parse unittests output trying to find the failed tests"""
    failed_tests = set()
    for test in set_of_tests:
        if test in unittests_output:
            failed_tests.add(test)
    return failed_tests


def skip_if_not_running_from_android_device(func):
    """
    Skip run of the function in case that we are running the app form android.

    .. note:: this is useful for some kind of tests that are supposed to be run
              from an android device and relies on `pyjnius`.
    """

    def wrapper(*arg, **kwarg):
        if RUNNING_ON_ANDROID:
            return func(*arg, **kwarg)
        raise_error(
            'Function `{func_name}` only available for android devices'.format(
                func_name=func.__name__,
            ),
        )
        return None

    return wrapper


@skip_if_not_running_from_android_device
def get_android_python_activity():
    """
    Return the `PythonActivity.mActivity` using `pyjnius`.

    .. warning:: This function will only be ran if executed from android"""
    from jnius import autoclass

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    return PythonActivity.mActivity


@skip_if_not_running_from_android_device
def vibrate_with_pyjnius(time=1000):
    """
    Vibrate an android device using `pyjnius`.

    .. warning:: This function will only be ran if executed from android."""
    from jnius import autoclass, cast

    print('Attempting to vibrate with pyjnius')
    ANDROID_VERSION = autoclass('android.os.Build$VERSION')
    SDK_INT = ANDROID_VERSION.SDK_INT

    Context = autoclass("android.content.Context")
    activity = get_android_python_activity()

    vibrator_service = activity.getSystemService(Context.VIBRATOR_SERVICE)
    vibrator = cast("android.os.Vibrator", vibrator_service)

    if vibrator and SDK_INT >= 26:
        print("Using android's `VibrationEffect` (SDK >= 26)")
        VibrationEffect = autoclass("android.os.VibrationEffect")
        vibrator.vibrate(
            VibrationEffect.createOneShot(
                time, VibrationEffect.DEFAULT_AMPLITUDE,
            ),
        )
    elif vibrator:
        print("Using deprecated android's vibrate (SDK < 26)")
        vibrator.vibrate(time)
    else:
        print('Something happened...vibrator service disabled?')


@skip_if_not_running_from_android_device
def set_device_orientation(direction):
    """
    Modifies the app orientation for an android device.

    .. warning:: This function will only be ran if executed from android."""
    if direction not in ('sensor', 'horizontal', 'vertical'):
        print(
            'ERROR: asked to orient to `{direction}`, but we only support: '
            'sensor, horizontal or vertical'.format(direction=direction)
        )
    from jnius import autoclass

    activity = get_android_python_activity()
    ActivityInfo = autoclass('android.content.pm.ActivityInfo')

    if direction == 'sensor':
        activity.setRequestedOrientation(
            ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED)
    elif direction == 'horizontal':
        activity.setRequestedOrientation(
            ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE)
    else:
        activity.setRequestedOrientation(
            ActivityInfo.SCREEN_ORIENTATION_PORTRAIT)


@skip_if_not_running_from_android_device
def setup_lifecycle_callbacks():
    """
    Register example ActivityLifecycleCallbacks
    """
    from android.activity import register_activity_lifecycle_callbacks

    register_activity_lifecycle_callbacks(
        onActivityStarted=lambda activity: print('onActivityStarted'),
        onActivityPaused=lambda activity: print('onActivityPaused'),
        onActivityResumed=lambda activity: print('onActivityResumed'),
        onActivityStopped=lambda activity: print('onActivityStopped'),
        onActivityDestroyed=lambda activity: print('onActivityDestroyed'),
    )
