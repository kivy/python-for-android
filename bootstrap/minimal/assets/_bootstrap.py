"""
Python minimal bootstrap
========================

This is the file extracted from the APK assets, and directly executed.
The bootstrap handle the execution of the main.py application file, and
correctly set the sys.path, logs, site, etc.

The minimal bootstrap prefer to put all the python into the assets directory,
uncompressed (aapt might compress). So we need to do few tricks do be able to
start without uncompressing all the data.
"""

import sys
import androidembed
import posix
from zipimport import zipimporter


def extract_asset(apk, asset_fn, dest_fn):
    # This function can be called only after step 2
    from os.path import exists, dirname
    from os import makedirs

    dest_dir = dirname(dest_fn)
    if not exists(dest_dir):
        makedirs(dest_dir)
    with open(dest_fn, "wb") as fd:
        data = apk.get_data("assets/" + asset_fn)
        fd.write(data)


#
# Step 1: redirect all the stdout/stderr to Android log.
#

class LogFile(object):

    def __init__(self):
        self._buf = ''

    def write(self, message):
        message = self._buf + message
        lines = message.split("\n")
        for line in lines[:-1]:
            androidembed.log(line)
        self._buf = lines[-1]

    def flush(self):
        return

sys.stdout = sys.stderr = LogFile()


#
# Step 2: rewrite the sys.path to use the APK assets as source
#

android_apk_fn = posix.environ["ANDROID_APK_FN"]
pylib_path = "{}/assets/lib/python2.7/".format(android_apk_fn)
sys.path[:] = [p.format(android_apk_fn) for p in [
    "{}/assets",
    "{}/assets/lib/python2.7/",
    "{}/assets/lib/python2.7/site-packages/"]]


#
# Step 3: Python needs the Makefile and pyconfig.h to be able to import site
#

data_path = posix.environ["ANDROID_INTERNAL_DATA_PATH"]
makefile_fn = "{}/python2.7/lib/config/Makefile".format(data_path)
pyconfig_fn = "{}/python2.7/include/pyconfig.h".format(data_path)

# extract both makefile and config
apk = zipimporter(posix.environ["ANDROID_APK_FN"])
extract_asset(apk, "lib/python2.7/config/Makefile", makefile_fn)
extract_asset(apk, "include/python2.7/pyconfig.h", pyconfig_fn)

# ensure sysconfig will find our file
import sysconfig
sysconfig._get_makefile_filename = lambda: makefile_fn
sysconfig.get_config_h_filename = lambda: pyconfig_fn


#
# Step 4: install a custom importer
#

import imp
from os.path import join, exists

ANDROID_LIB_PATH = posix.environ["ANDROID_LIB_PATH"]


class CustomBuiltinImporter(object):
    def find_module(self, fullname, mpath=None):
        modname = "libpy_{}.so".format(fullname.replace(".", "_"))
        modfn = join(ANDROID_LIB_PATH, modname)
        if exists(modfn):
            return self

    def load_module(self, fullname):
        fn = fullname.replace(".", "_")
        mod = sys.modules.get(fn)
        if mod is None:
            try:
                mod = imp.load_dynamic(
                    fn,
                    join(ANDROID_LIB_PATH, "libpy_{}.so".format(fn)))
            except ImportError:
                # untested part, similar to iOS custom importer.
                mod = imp.load_dynamic(fullname, fullname)
        return mod

sys.meta_path.append(CustomBuiltinImporter())


#
# Step 4: bootstrap the application !
#

import runpy
runpy._run_module_as_main("main", False)
