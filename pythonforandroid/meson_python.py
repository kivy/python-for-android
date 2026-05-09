import sys
import json
import subprocess
import importlib.util
from os.path import join
from glob import glob


class C:
    TARGET_PYTHON_PREFIX = globals().get("TARGET_PYTHON_PREFIX")
    PYTHON_MAJOR_VERSION = globals().get("PYTHON_MAJOR_VERSION", sys.version_info.major)
    PYTHON_MINOR_VERSION = globals().get("PYTHON_MINOR_VERSION", sys.version_info.minor)
    PLATFORM_TAG = globals().get("PLATFORM_TAG", sys.platform)
    PYTHON_SUFFIX = globals().get("PYTHON_SUFFIX", "")


def handle_python_info():

    prefix = C.TARGET_PYTHON_PREFIX

    sysconfig_file = glob(join(prefix, f"lib/python{C.PYTHON_MAJOR_VERSION}.{C.PYTHON_MINOR_VERSION}/_sysconfigdata*.py"))[0]

    spec = importlib.util.spec_from_file_location("_android_cfg", sysconfig_file)
    cfg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg)

    ver_python = f"python{C.PYTHON_MAJOR_VERSION}.{C.PYTHON_MINOR_VERSION}"

    site_path = join(prefix, f"lib/{ver_python}/site-packages")

    android_paths = {
        "stdlib": join(prefix, "lib"),
        "platstdlib": join(prefix, "lib"),
        "purelib": site_path,
        "platlib": site_path,
        "include": join(prefix, f"include/{ver_python}/"),
        "platinclude": join(prefix, f"include/{ver_python}/"),
        "scripts": join(prefix, "bin"),
        "data": prefix,
    }

    print(
        json.dumps(
            {
                "variables": cfg.build_time_vars,
                "paths": android_paths,
                "sysconfig_paths": android_paths,
                "install_paths": android_paths,
                "version": f"{C.PYTHON_MAJOR_VERSION}.{C.PYTHON_MINOR_VERSION}",
                "platform": C.PLATFORM_TAG,
                "is_pypy": False,
                "is_venv": False,
                "link_libpython": True,
                "suffix": C.PYTHON_SUFFIX,
                "limited_api_suffix": ".abi3.so",
                "is_freethreaded": False,
            }
        )
    )


WHITELIST = {
    "python_info.py": handle_python_info,
}


args = sys.argv[1:]

if args:
    cmd = args[0]
    name = cmd.split("/")[-1]

    if name in WHITELIST:
        sys.exit(WHITELIST[name]())

sys.exit(subprocess.run([sys.executable] + args).returncode)
