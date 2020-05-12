
import os


def get_activity_lib_dir(activity_name):
    from jnius import autoclass

    # Get the actual activity instance:
    activity_class = autoclass(activity_name)
    if activity_class is None:
        return None
    activity = None
    if hasattr(activity_class, "mActivity") and \
            activity_class.mActivity is not None:
        activity = activity_class.mActivity
    elif hasattr(activity_class, "mService") and \
            activity_class.mService is not None:
        activity = activity_class.mService
    if activity is None:
        return None

    # Extract the native lib dir from the activity instance:
    package_name = activity.getApplicationContext().getPackageName()
    manager = activity.getApplicationContext().getPackageManager()
    manager_class = autoclass("android.content.pm.PackageManager")
    native_lib_dir = manager.getApplicationInfo(
        package_name, manager_class.GET_SHARED_LIBRARY_FILES
    ).nativeLibraryDir
    return native_lib_dir


def does_libname_match_filename(search_name, file_path):
    # Filter file names so given search_name="mymodule" we match one of:
    #      mymodule.so         (direct name + .so)
    #      libmymodule.so      (added lib prefix)
    #      mymodule.arm64.so   (added dot-separated middle parts)
    #      mymodule.so.1.3.4   (added dot-separated version tail)
    #      and all above       (all possible combinations)
    import re
    file_name = os.path.basename(file_path)
    return (re.match(r"^(lib)?" + re.escape(search_name) +
                     r"\.(.*\.)?so(\.[0-9]+)*$", file_name) is not None)


def find_library(name):
    # Obtain all places for native libraries:
    lib_search_dirs = ["/system/lib"]
    lib_dir_1 = get_activity_lib_dir("org.kivy.android.PythonActivity")
    if lib_dir_1 is not None:
        lib_search_dirs.insert(0, lib_dir_1)
    lib_dir_2 = get_activity_lib_dir("org.kivy.android.PythonService")
    if lib_dir_2 is not None and lib_dir_2 not in lib_search_dirs:
        lib_search_dirs.insert(0, lib_dir_2)

    # Now scan the lib dirs:
    for lib_dir in [ldir for ldir in lib_search_dirs if os.path.exists(ldir)]:
        filelist = [
            f for f in os.listdir(lib_dir)
            if does_libname_match_filename(name, f)
        ]
        if len(filelist) > 0:
            return os.path.join(lib_dir, filelist[0])
    return None
