
# This test is still expected to support Python 2, as it tests
# on-Android functionality that we still maintain
try:  # Python 3+
    from unittest import mock
    from unittest.mock import MagicMock
except ImportError:  # Python 2
    import mock
    from mock import MagicMock
import os
import shutil
import sys
import tempfile


# Import the tested android._ctypes_library_finder module,
# making sure android._android won't crash us!
# (since android._android is android-only / not compilable on desktop)
android_module_folder = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "..", "pythonforandroid", "recipes", "android", "src"
))
sys.path.insert(0, android_module_folder)
sys.modules['android._android'] = MagicMock()
import android._ctypes_library_finder
sys.path.remove(android_module_folder)


@mock.patch.dict('sys.modules', jnius=MagicMock())
def test_get_activity_lib_dir():
    import jnius  # should get us our fake module

    # Short test that it works when activity doesn't exist:
    jnius.autoclass = MagicMock()
    jnius.autoclass.return_value = None
    assert android._ctypes_library_finder.get_activity_lib_dir(
        "JavaClass"
    ) is None
    assert mock.call("JavaClass") in jnius.autoclass.call_args_list

    # Comprehensive test that verifies getApplicationInfo() call:
    activity = MagicMock()
    app_context = activity.getApplicationContext()
    app_context.getPackageName.return_value = "test.package"
    app_info = app_context.getPackageManager().getApplicationInfo()
    app_info.nativeLibraryDir = '/testpath'

    def pick_class(name):
        cls = MagicMock()
        if name == "JavaClass":
            cls.mActivity = activity
        elif name == "android.content.pm.PackageManager":
            # Manager class:
            cls.GET_SHARED_LIBRARY_FILES = 1024
        return cls

    jnius.autoclass = MagicMock(side_effect=pick_class)
    assert android._ctypes_library_finder.get_activity_lib_dir(
        "JavaClass"
    ) == "/testpath"
    assert mock.call("JavaClass") in jnius.autoclass.call_args_list
    assert mock.call("test.package", 1024) in (
        app_context.getPackageManager().getApplicationInfo.call_args_list
    )


@mock.patch.dict('sys.modules', jnius=MagicMock())
def test_find_library():
    test_d = tempfile.mkdtemp(prefix="p4a-android-ctypes-test-libdir-")
    try:
        with open(os.path.join(test_d, "mymadeuplib.so.5"), "w"):
            pass
        import jnius  # should get us our fake module

        # Test with mActivity returned:
        jnius.autoclass = MagicMock()
        jnius.autoclass().mService = None
        app_context = jnius.autoclass().mActivity.getApplicationContext()
        app_info = app_context.getPackageManager().getApplicationInfo()
        app_info.nativeLibraryDir = '/doesnt-exist-testpath'
        assert android._ctypes_library_finder.find_library(
            "mymadeuplib"
        ) is None
        assert mock.call("org.kivy.android.PythonActivity") in (
            jnius.autoclass.call_args_list
        )
        app_info.nativeLibraryDir = test_d
        assert os.path.normpath(android._ctypes_library_finder.find_library(
            "mymadeuplib"
        )) == os.path.normpath(os.path.join(test_d, "mymadeuplib.so.5"))

        # Test with mService returned:
        jnius.autoclass = MagicMock()
        jnius.autoclass().mActivity = None
        app_context = jnius.autoclass().mService.getApplicationContext()
        app_info = app_context.getPackageManager().getApplicationInfo()
        app_info.nativeLibraryDir = '/doesnt-exist-testpath'
        assert android._ctypes_library_finder.find_library(
            "mymadeuplib"
        ) is None
        app_info.nativeLibraryDir = test_d
        assert os.path.normpath(android._ctypes_library_finder.find_library(
            "mymadeuplib"
        )) == os.path.normpath(os.path.join(test_d, "mymadeuplib.so.5"))
    finally:
        shutil.rmtree(test_d)


def test_does_libname_match_filename():
    assert android._ctypes_library_finder.does_libname_match_filename(
        "mylib", "mylib.so"
    )
    assert not android._ctypes_library_finder.does_libname_match_filename(
        "mylib", "amylib.so"
    )
    assert not android._ctypes_library_finder.does_libname_match_filename(
        "mylib", "mylib.txt"
    )
    assert not android._ctypes_library_finder.does_libname_match_filename(
        "mylib", "mylib"
    )
    assert android._ctypes_library_finder.does_libname_match_filename(
        "mylib", "libmylib.test.so.1.2.3"
    )
    assert not android._ctypes_library_finder.does_libname_match_filename(
        "mylib", "libtest.mylib.so"
    )
    assert android._ctypes_library_finder.does_libname_match_filename(
        "mylib", "mylib.so.5"
    )
