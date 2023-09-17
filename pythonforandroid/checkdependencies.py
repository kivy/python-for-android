from importlib import import_module
from os import environ
import sys

from packaging.version import Version

from pythonforandroid.prerequisites import (
    check_and_install_default_prerequisites,
)


def check_python_dependencies():
    """
    Check if the Python requirements are installed. This must appears
    before other imports because otherwise they're imported elsewhere.

    Using the ok check instead of failing immediately so that all
    errors are printed at once.
    """

    ok = True

    modules = [("colorama", "0.3.3"), "appdirs", ("sh", "1.10"), "jinja2"]

    for module in modules:
        if isinstance(module, tuple):
            module, version = module
        else:
            version = None

        try:
            import_module(module)
        except ImportError:
            if version is None:
                print(
                    "ERROR: The {} Python module could not be found, please "
                    "install it.".format(module)
                )
                ok = False
            else:
                print(
                    "ERROR: The {} Python module could not be found, "
                    "please install version {} or higher".format(
                        module, version
                    )
                )
                ok = False
        else:
            if version is None:
                continue
            try:
                cur_ver = sys.modules[module].__version__
            except AttributeError:  # this is sometimes not available
                continue
            if Version(cur_ver) < Version(version):
                print(
                    "ERROR: {} version is {}, but python-for-android needs "
                    "at least {}.".format(module, cur_ver, version)
                )
                ok = False

    if not ok:
        print("python-for-android is exiting due to the errors logged above")
        exit(1)


def check():
    if not environ.get("SKIP_PREREQUISITES_CHECK", "0") == "1":
        check_and_install_default_prerequisites()
    check_python_dependencies()
