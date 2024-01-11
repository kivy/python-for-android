#!/usr/bin/env python3

from gzip import GzipFile
import hashlib
import json
from os.path import (
    dirname, join, isfile, realpath,
    relpath, split, exists, basename
)
from os import environ, listdir, makedirs, remove
import os
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

from fnmatch import fnmatch
import jinja2

from pythonforandroid.util import rmdir, ensure_dir, max_build_tool_version


def get_dist_info_for(key, error_if_missing=True):
    try:
        with open(join(dirname(__file__), 'dist_info.json'), 'r') as fileh:
            info = json.load(fileh)
        value = info[key]
    except (OSError, KeyError) as e:
        if not error_if_missing:
            return None
        print("BUILD FAILURE: Couldn't extract the key `" + key + "` " +
              "from dist_info.json: " + str(e))
        sys.exit(1)
    return value


def get_hostpython():
    return get_dist_info_for('hostpython')


def get_bootstrap_name():
    return get_dist_info_for('bootstrap')


if os.name == 'nt':
    ANDROID = 'android.bat'
    ANT = 'ant.bat'
else:
    ANDROID = 'android'
    ANT = 'ant'

curdir = dirname(__file__)

BLACKLIST_PATTERNS = [
    # code versionning
    '^*.hg/*',
    '^*.git/*',
    '^*.bzr/*',
    '^*.svn/*',

    # temp files
    '~',
    '*.bak',
    '*.swp',

    # Android artifacts
    '*.apk',
    '*.aab',
]

WHITELIST_PATTERNS = []

if os.environ.get("P4A_BUILD_IS_RUNNING_UNITTESTS", "0") != "1":
    PYTHON = get_hostpython()
    _bootstrap_name = get_bootstrap_name()
else:
    PYTHON = "python3"
    _bootstrap_name = "sdl2"

if PYTHON is not None and not exists(PYTHON):
    PYTHON = None

if _bootstrap_name in ('sdl2', 'webview', 'service_only', 'qt'):
    WHITELIST_PATTERNS.append('pyconfig.h')

environment = jinja2.Environment(loader=jinja2.FileSystemLoader(
    join(curdir, 'templates')))


DEFAULT_PYTHON_ACTIVITY_JAVA_CLASS = 'org.kivy.android.PythonActivity'
DEFAULT_PYTHON_SERVICE_JAVA_CLASS = 'org.kivy.android.PythonService'


def render(template, dest, **kwargs):
    '''Using jinja2, render `template` to the filename `dest`, supplying the

    keyword arguments as template parameters.
    '''

    dest_dir = dirname(dest)
    if dest_dir and not exists(dest_dir):
        makedirs(dest_dir)

    template = environment.get_template(template)
    text = template.render(**kwargs)

    f = open(dest, 'wb')
    f.write(text.encode('utf-8'))
    f.close()


def is_whitelist(name):
    return match_filename(WHITELIST_PATTERNS, name)


def is_blacklist(name):
    if is_whitelist(name):
        return False
    return match_filename(BLACKLIST_PATTERNS, name)


def match_filename(pattern_list, name):
    for pattern in pattern_list:
        if pattern.startswith('^'):
            pattern = pattern[1:]
        else:
            pattern = '*/' + pattern
        if fnmatch(name, pattern):
            return True


def listfiles(d):
    basedir = d
    subdirlist = []
    for item in os.listdir(d):
        fn = join(d, item)
        if isfile(fn):
            yield fn
        else:
            subdirlist.append(join(basedir, item))
    for subdir in subdirlist:
        for fn in listfiles(subdir):
            yield fn


def make_tar(tfn, source_dirs, byte_compile_python=False, optimize_python=True):
    '''
    Make a zip file `fn` from the contents of source_dis.
    '''

    def clean(tinfo):
        """cleaning function (for reproducible builds)"""
        tinfo.uid = tinfo.gid = 0
        tinfo.uname = tinfo.gname = ''
        tinfo.mtime = 0
        return tinfo

    # get the files and relpath file of all the directory we asked for
    files = []
    for sd in source_dirs:
        sd = realpath(sd)
        for fn in listfiles(sd):
            if is_blacklist(fn):
                continue
            if fn.endswith('.py') and byte_compile_python:
                fn = compile_py_file(fn, optimize_python=optimize_python)
            files.append((fn, relpath(realpath(fn), sd)))
    files.sort()  # deterministic

    # create tar.gz of thoses files
    gf = GzipFile(tfn, 'wb', mtime=0)  # deterministic
    tf = tarfile.open(None, 'w', gf, format=tarfile.USTAR_FORMAT)
    dirs = []
    for fn, afn in files:
        dn = dirname(afn)
        if dn not in dirs:
            # create every dirs first if not exist yet
            d = ''
            for component in split(dn):
                d = join(d, component)
                if d.startswith('/'):
                    d = d[1:]
                if d == '' or d in dirs:
                    continue
                dirs.append(d)
                tinfo = tarfile.TarInfo(d)
                tinfo.type = tarfile.DIRTYPE
                clean(tinfo)
                tf.addfile(tinfo)

        # put the file
        tf.add(fn, afn, filter=clean)
    tf.close()
    gf.close()


def compile_py_file(python_file, optimize_python=True):
    '''
    Compile python_file to *.pyc and return the filename of the *.pyc file.
    '''

    if PYTHON is None:
        return

    args = [PYTHON, '-m', 'compileall', '-b', '-f', python_file]
    if optimize_python:
        # -OO = strip docstrings
        args.insert(1, '-OO')
    return_code = subprocess.call(args)

    if return_code != 0:
        print('Error while running "{}"'.format(' '.join(args)))
        print('This probably means one of your Python files has a syntax '
              'error, see logs above')
        exit(1)

    return ".".join([os.path.splitext(python_file)[0], "pyc"])


def make_package(args):
    # If no launcher is specified, require a main.py/main.pyc:
    if (get_bootstrap_name() != "sdl" or args.launcher is None) and \
            get_bootstrap_name() not in ["webview", "service_library"]:
        # (webview doesn't need an entrypoint, apparently)
        if args.private is None or (
                not exists(join(realpath(args.private), 'main.py')) and
                not exists(join(realpath(args.private), 'main.pyc'))):
            print('''BUILD FAILURE: No main.py(c) found in your app directory. This
file must exist to act as the entry point for you app. If your app is
started by a file with a different name, rename it to main.py or add a
main.py that loads it.''')
            sys.exit(1)

    assets_dir = "src/main/assets"

    # Delete the old assets.
    rmdir(assets_dir, ignore_errors=True)
    ensure_dir(assets_dir)

    # Add extra environment variable file into tar-able directory:
    env_vars_tarpath = tempfile.mkdtemp(prefix="p4a-extra-env-")
    with open(os.path.join(env_vars_tarpath, "p4a_env_vars.txt"), "w") as f:
        if hasattr(args, "window"):
            f.write("P4A_IS_WINDOWED=" + str(args.window) + "\n")
        if hasattr(args, "sdl_orientation_hint"):
            f.write("KIVY_ORIENTATION=" + str(args.sdl_orientation_hint) + "\n")
        f.write("P4A_NUMERIC_VERSION=" + str(args.numeric_version) + "\n")
        f.write("P4A_MINSDK=" + str(args.min_sdk_version) + "\n")

    # Package up the private data (public not supported).
    use_setup_py = get_dist_info_for("use_setup_py",
                                     error_if_missing=False) is True
    private_tar_dirs = [env_vars_tarpath]
    _temp_dirs_to_clean = []
    try:
        if args.private:
            if not use_setup_py or (
                    not exists(join(args.private, "setup.py")) and
                    not exists(join(args.private, "pyproject.toml"))
                    ):
                print('No setup.py/pyproject.toml used, copying '
                      'full private data into .apk.')
                private_tar_dirs.append(args.private)
            else:
                print("Copying main.py's ONLY, since other app data is "
                      "expected in site-packages.")
                main_py_only_dir = tempfile.mkdtemp()
                _temp_dirs_to_clean.append(main_py_only_dir)

                # Check all main.py files we need to copy:
                copy_paths = ["main.py", join("service", "main.py")]
                for copy_path in copy_paths:
                    variants = [
                        copy_path,
                        copy_path.partition(".")[0] + ".pyc",
                    ]
                    # Check in all variants with all possible endings:
                    for variant in variants:
                        if exists(join(args.private, variant)):
                            # Make sure surrounding directly exists:
                            dir_path = os.path.dirname(variant)
                            if (len(dir_path) > 0 and
                                    not exists(
                                        join(main_py_only_dir, dir_path)
                                    )):
                                ensure_dir(join(main_py_only_dir, dir_path))
                            # Copy actual file:
                            shutil.copyfile(
                                join(args.private, variant),
                                join(main_py_only_dir, variant),
                            )

                # Append directory with all main.py's to result apk paths:
                private_tar_dirs.append(main_py_only_dir)
        if get_bootstrap_name() == "webview":
            for asset in listdir('webview_includes'):
                shutil.copy(join('webview_includes', asset), join(assets_dir, asset))

        for asset in args.assets:
            asset_src, asset_dest = asset.split(":")
            if isfile(realpath(asset_src)):
                ensure_dir(dirname(join(assets_dir, asset_dest)))
                shutil.copy(realpath(asset_src), join(assets_dir, asset_dest))
            else:
                shutil.copytree(realpath(asset_src), join(assets_dir, asset_dest))

        if args.private or args.launcher:
            for arch in get_dist_info_for("archs"):
                libs_dir = f"libs/{arch}"
                make_tar(
                    join(libs_dir, "libpybundle.so"),
                    [f"_python_bundle__{arch}"],
                    byte_compile_python=args.byte_compile_python,
                    optimize_python=args.optimize_python,
                )
            make_tar(
                join(assets_dir, "private.tar"),
                private_tar_dirs,
                byte_compile_python=args.byte_compile_python,
                optimize_python=args.optimize_python,
            )
    finally:
        for directory in _temp_dirs_to_clean:
            rmdir(directory)

    # Remove extra env vars tar-able directory:
    rmdir(env_vars_tarpath)

    # Prepare some variables for templating process
    res_dir = "src/main/res"
    res_dir_initial = "src/res_initial"
    # make res_dir stateless
    if exists(res_dir_initial):
        rmdir(res_dir, ignore_errors=True)
        shutil.copytree(res_dir_initial, res_dir)
    else:
        shutil.copytree(res_dir, res_dir_initial)

    # Add user resouces
    for resource in args.resources:
        resource_src, resource_dest = resource.split(":")
        if isfile(realpath(resource_src)):
            ensure_dir(dirname(join(res_dir, resource_dest)))
            shutil.copy(realpath(resource_src), join(res_dir, resource_dest))
        else:
            shutil.copytree(realpath(resource_src),
                            join(res_dir, resource_dest), dirs_exist_ok=True)

    default_icon = 'templates/kivy-icon.png'
    default_presplash = 'templates/kivy-presplash.jpg'
    shutil.copy(
        args.icon or default_icon,
        join(res_dir, 'mipmap/icon.png')
    )
    if args.icon_fg and args.icon_bg:
        shutil.copy(args.icon_fg, join(res_dir, 'mipmap/icon_foreground.png'))
        shutil.copy(args.icon_bg, join(res_dir, 'mipmap/icon_background.png'))
        with open(join(res_dir, 'mipmap-anydpi-v26/icon.xml'), "w") as fd:
            fd.write("""<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@mipmap/icon_background"/>
    <foreground android:drawable="@mipmap/icon_foreground"/>
</adaptive-icon>
""")
    elif args.icon_fg or args.icon_bg:
        print("WARNING: Received an --icon_fg or an --icon_bg argument, but not both. "
              "Ignoring.")

    if get_bootstrap_name() != "service_only":
        lottie_splashscreen = join(res_dir, 'raw/splashscreen.json')
        if args.presplash_lottie:
            shutil.copy(
                'templates/lottie.xml',
                join(res_dir, 'layout/lottie.xml')
            )
            ensure_dir(join(res_dir, 'raw'))
            shutil.copy(
                args.presplash_lottie,
                join(res_dir, 'raw/splashscreen.json')
            )
        else:
            if exists(lottie_splashscreen):
                remove(lottie_splashscreen)
                remove(join(res_dir, 'layout/lottie.xml'))

            shutil.copy(
                args.presplash or default_presplash,
                join(res_dir, 'drawable/presplash.jpg')
            )

    # If extra Java jars were requested, copy them into the libs directory
    jars = []
    if args.add_jar:
        for jarname in args.add_jar:
            if not exists(jarname):
                print('Requested jar does not exist: {}'.format(jarname))
                sys.exit(-1)
            shutil.copy(jarname, 'src/main/libs')
            jars.append(basename(jarname))

    # If extra aar were requested, copy them into the libs directory
    aars = []
    if args.add_aar:
        ensure_dir("libs")
        for aarname in args.add_aar:
            if not exists(aarname):
                print('Requested aar does not exists: {}'.format(aarname))
                sys.exit(-1)
            shutil.copy(aarname, 'libs')
            aars.append(basename(aarname).rsplit('.', 1)[0])

    versioned_name = (args.name.replace(' ', '').replace('\'', '') +
                      '-' + args.version)

    version_code = 0
    if not args.numeric_version:
        """
        Set version code in format (10 + minsdk + app_version)
        Historically versioning was (arch + minsdk + app_version),
        with arch expressed with a single digit from 6 to 9.
        Since the multi-arch support, has been changed to 10.
        """
        min_sdk = args.min_sdk_version
        for i in args.version.split('.'):
            version_code *= 100
            version_code += int(i)
        args.numeric_version = "{}{}{}".format("10", min_sdk, version_code)

    if args.intent_filters:
        with open(args.intent_filters) as fd:
            args.intent_filters = fd.read()

    if not args.add_activity:
        args.add_activity = []

    if not args.activity_launch_mode:
        args.activity_launch_mode = ''

    if args.extra_source_dirs:
        esd = []
        for spec in args.extra_source_dirs:
            if ':' in spec:
                specdir, specincludes = spec.split(':')
                print('WARNING: Currently gradle builds only support including source '
                      'directories, so when building using gradle all files in '
                      '{} will be included.'.format(specdir))
            else:
                specdir = spec
                specincludes = '**'
            esd.append((realpath(specdir), specincludes))
        args.extra_source_dirs = esd
    else:
        args.extra_source_dirs = []

    service = False
    if args.private:
        service_main = join(realpath(args.private), 'service', 'main.py')
        if exists(service_main) or exists(service_main + 'o'):
            service = True

    service_names = []
    base_service_class = args.service_class_name.split('.')[-1]
    for sid, spec in enumerate(args.services):
        spec = spec.split(':')
        name = spec[0]
        entrypoint = spec[1]
        options = spec[2:]

        foreground = 'foreground' in options
        sticky = 'sticky' in options

        service_names.append(name)
        service_target_path =\
            'src/main/java/{}/Service{}.java'.format(
                args.package.replace(".", "/"),
                name.capitalize()
            )
        render(
            'Service.tmpl.java',
            service_target_path,
            name=name,
            entrypoint=entrypoint,
            args=args,
            foreground=foreground,
            sticky=sticky,
            service_id=sid + 1,
            base_service_class=base_service_class,
        )

    # Find the SDK directory and target API
    with open('project.properties', 'r') as fileh:
        target = fileh.read().strip()
    android_api = target.split('-')[1]

    if android_api.isdigit():
        android_api = int(android_api)
    else:
        raise ValueError(
            "failed to extract the Android API level from " +
            "build.properties. expected int, got: '" +
            str(android_api) + "'"
        )

    with open('local.properties', 'r') as fileh:
        sdk_dir = fileh.read().strip()
    sdk_dir = sdk_dir[8:]

    # Try to build with the newest available build tools
    ignored = {".DS_Store", ".ds_store"}
    build_tools_versions = [x for x in listdir(join(sdk_dir, 'build-tools')) if x not in ignored]
    build_tools_version = max_build_tool_version(build_tools_versions)

    # Folder name for launcher (used by SDL2 bootstrap)
    url_scheme = 'kivy'

    # Copy backup rules file if specified and update the argument
    res_xml_dir = join(res_dir, 'xml')
    if args.backup_rules:
        ensure_dir(res_xml_dir)
        shutil.copy(join(args.private, args.backup_rules), res_xml_dir)
        args.backup_rules = split(args.backup_rules)[1][:-4]

    # Copy res_xml files to src/main/res/xml
    if args.res_xmls:
        ensure_dir(res_xml_dir)
        for xmlpath in args.res_xmls:
            if not os.path.exists(xmlpath):
                xmlpath = join(args.private, xmlpath)
            shutil.copy(xmlpath, res_xml_dir)

    # Render out android manifest:
    manifest_path = "src/main/AndroidManifest.xml"
    render_args = {
        "args": args,
        "service": service,
        "service_names": service_names,
        "android_api": android_api,
        "debug": "debug" in args.build_mode,
        "native_services": args.native_services
    }
    if get_bootstrap_name() == "sdl2":
        render_args["url_scheme"] = url_scheme

    render(
        'AndroidManifest.tmpl.xml',
        manifest_path,
        **render_args)

    # Copy the AndroidManifest.xml to the dist root dir so that ant
    # can also use it
    if exists('AndroidManifest.xml'):
        remove('AndroidManifest.xml')
    shutil.copy(manifest_path, 'AndroidManifest.xml')

    # gradle build templates
    render(
        'build.tmpl.gradle',
        'build.gradle',
        args=args,
        aars=aars,
        jars=jars,
        android_api=android_api,
        build_tools_version=build_tools_version,
        debug_build="debug" in args.build_mode,
        is_library=(get_bootstrap_name() == 'service_library'),
        )

    # gradle properties
    render(
        'gradle.tmpl.properties',
        'gradle.properties',
        args=args,
        bootstrap_name=get_bootstrap_name())

    # ant build templates
    render(
        'build.tmpl.xml',
        'build.xml',
        args=args,
        versioned_name=versioned_name)

    # String resources:
    timestamp = time.time()
    if 'SOURCE_DATE_EPOCH' in environ:
        # for reproducible builds
        timestamp = int(environ['SOURCE_DATE_EPOCH'])
    private_version = "{} {} {}".format(
        args.version,
        args.numeric_version,
        timestamp
    )
    render_args = {
        "args": args,
        "private_version": hashlib.sha1(private_version.encode()).hexdigest()
    }
    if get_bootstrap_name() == "sdl2":
        render_args["url_scheme"] = url_scheme
    render(
        'strings.tmpl.xml',
        join(res_dir, 'values/strings.xml'),
        **render_args)

    # Library resources from Qt
    # These are referred by QtLoader.java in Qt6AndroidBindings.jar
    # qt_libs and load_local_libs are loaded at App startup
    if get_bootstrap_name() == "qt":
        qt_libs = args.qt_libs.split(",")
        load_local_libs = args.load_local_libs.split(",")
        init_classes = args.init_classes
        if init_classes:
            init_classes = init_classes.split(",")
            init_classes = ":".join(init_classes)
        arch = get_dist_info_for("archs")[0]
        render(
            'libs.tmpl.xml',
            join(res_dir, 'values/libs.xml'),
            qt_libs=qt_libs,
            load_local_libs=load_local_libs,
            init_classes=init_classes,
            arch=arch
        )

    if exists(join("templates", "custom_rules.tmpl.xml")):
        render(
            'custom_rules.tmpl.xml',
            'custom_rules.xml',
            args=args)

    if get_bootstrap_name() == "webview":
        render('WebViewLoader.tmpl.java',
               'src/main/java/org/kivy/android/WebViewLoader.java',
               args=args)

    if args.sign:
        render('build.properties', 'build.properties')
    else:
        if exists('build.properties'):
            os.remove('build.properties')

    # Apply java source patches if any are present:
    if exists(join('src', 'patches')):
        print("Applying Java source code patches...")
        for patch_name in os.listdir(join('src', 'patches')):
            patch_path = join('src', 'patches', patch_name)
            print("Applying patch: " + str(patch_path))

            # -N: insist this is FORWARD patch, don't reverse apply
            # -p1: strip first path component
            # -t: batch mode, don't ask questions
            patch_command = ["patch", "-N", "-p1", "-t", "-i", patch_path]

            try:
                # Use a dry run to establish whether the patch is already applied.
                # If we don't check this, the patch may be partially applied (which is bad!)
                subprocess.check_output(patch_command + ["--dry-run"])
            except subprocess.CalledProcessError as e:
                if e.returncode == 1:
                    # Return code 1 means not all hunks could be applied, this usually
                    # means the patch is already applied.
                    print("Warning: failed to apply patch (exit code 1), "
                          "assuming it is already applied: ",
                          str(patch_path))
                else:
                    raise e
            else:
                # The dry run worked, so do the real thing
                subprocess.check_output(patch_command)


def parse_permissions(args_permissions):
    if args_permissions and isinstance(args_permissions[0], list):
        args_permissions = [p for perm in args_permissions for p in perm]

    def _is_advanced_permission(permission):
        return permission.startswith("(") and permission.endswith(")")

    def _decode_advanced_permission(permission):
        SUPPORTED_PERMISSION_PROPERTIES = ["name", "maxSdkVersion", "usesPermissionFlags"]
        _permission_args = permission[1:-1].split(";")
        _permission_args = (arg.split("=") for arg in _permission_args)
        advanced_permission = dict(_permission_args)

        if "name" not in advanced_permission:
            raise ValueError("Advanced permission must have a name property")

        for key in advanced_permission.keys():
            if key not in SUPPORTED_PERMISSION_PROPERTIES:
                raise ValueError(
                    f"Property '{key}' is not supported. "
                    "Advanced permission only supports: "
                    f"{', '.join(SUPPORTED_PERMISSION_PROPERTIES)} properties"
                )

        return advanced_permission

    _permissions = []
    for permission in args_permissions:
        if _is_advanced_permission(permission):
            _permissions.append(_decode_advanced_permission(permission))
        else:
            if "." in permission:
                _permissions.append(dict(name=permission))
            else:
                _permissions.append(dict(name=f"android.permission.{permission}"))
    return _permissions


def get_sdl_orientation_hint(orientations):
    SDL_ORIENTATION_MAP = {
        "landscape": "LandscapeLeft",
        "portrait": "Portrait",
        "portrait-reverse": "PortraitUpsideDown",
        "landscape-reverse": "LandscapeRight",
    }
    return " ".join(
        [SDL_ORIENTATION_MAP[x] for x in orientations if x in SDL_ORIENTATION_MAP]
    )


def get_manifest_orientation(orientations, manifest_orientation=None):
    # If the user has specifically set an orientation to use in the manifest,
    # use that.
    if manifest_orientation is not None:
        return manifest_orientation

    # If multiple or no orientations are specified, use unspecified in the manifest,
    # as we can only specify one orientation in the manifest.
    if len(orientations) != 1:
        return "unspecified"

    # Convert the orientation to a value that can be used in the manifest.
    # If the specified orientation is not supported, use unspecified.
    MANIFEST_ORIENTATION_MAP = {
        "landscape": "landscape",
        "portrait": "portrait",
        "portrait-reverse": "reversePortrait",
        "landscape-reverse": "reverseLandscape",
    }
    return MANIFEST_ORIENTATION_MAP.get(orientations[0], "unspecified")


def get_dist_ndk_min_api_level():
    # Get the default minsdk, equal to the NDK API that this dist is built against
    try:
        with open('dist_info.json', 'r') as fileh:
            info = json.load(fileh)
            ndk_api = int(info['ndk_api'])
    except (OSError, KeyError, ValueError, TypeError):
        print('WARNING: Failed to read ndk_api from dist info, defaulting to 12')
        ndk_api = 12  # The old default before ndk_api was introduced
    return ndk_api


def create_argument_parser():
    ndk_api = get_dist_ndk_min_api_level()
    import argparse
    ap = argparse.ArgumentParser(description='''\
Package a Python application for Android (using
bootstrap ''' + get_bootstrap_name() + ''').

For this to work, Java and Ant need to be in your path, as does the
tools directory of the Android SDK.
''')

    # --private is required unless for sdl2, where there's also --launcher
    ap.add_argument('--private', dest='private',
                    help='the directory with the app source code files' +
                         ' (containing your main.py entrypoint)',
                    required=(get_bootstrap_name() != "sdl2"))
    ap.add_argument('--package', dest='package',
                    help=('The name of the java package the project will be'
                          ' packaged under.'),
                    required=True)
    ap.add_argument('--name', dest='name',
                    help=('The human-readable name of the project.'),
                    required=True)
    ap.add_argument('--numeric-version', dest='numeric_version',
                    help=('The numeric version number of the project. If not '
                          'given, this is automatically computed from the '
                          'version.'))
    ap.add_argument('--version', dest='version',
                    help=('The version number of the project. This should '
                          'consist of numbers and dots, and should have the '
                          'same number of groups of numbers as previous '
                          'versions.'),
                    required=True)
    if get_bootstrap_name() == "sdl2":
        ap.add_argument('--launcher', dest='launcher', action='store_true',
                        help=('Provide this argument to build a multi-app '
                              'launcher, rather than a single app.'))
        ap.add_argument('--home-app', dest='home_app', action='store_true', default=False,
                        help=('Turn your application into a home app (launcher)'))
    ap.add_argument('--permission', dest='permissions', action='append', default=[],
                    help='The permissions to give this app.', nargs='+')
    ap.add_argument('--meta-data', dest='meta_data', action='append', default=[],
                    help='Custom key=value to add in application metadata')
    ap.add_argument('--uses-library', dest='android_used_libs', action='append', default=[],
                    help='Used shared libraries included using <uses-library> tag in AndroidManifest.xml')
    ap.add_argument('--asset', dest='assets',
                    action="append", default=[],
                    metavar="/path/to/source:dest",
                    help='Put this in the assets folder at assets/dest')
    ap.add_argument('--resource', dest='resources',
                    action="append", default=[],
                    metavar="/path/to/source:kind/asset",
                    help='Put this in the res folder at res/kind')
    ap.add_argument('--icon', dest='icon',
                    help=('A png file to use as the icon for '
                          'the application.'))
    ap.add_argument('--icon-fg', dest='icon_fg',
                    help=('A png file to use as the foreground of the adaptive icon '
                          'for the application.'))
    ap.add_argument('--icon-bg', dest='icon_bg',
                    help=('A png file to use as the background of the adaptive icon '
                          'for the application.'))
    ap.add_argument('--service', dest='services', action='append', default=[],
                    help='Declare a new service entrypoint: '
                         'NAME:PATH_TO_PY[:foreground]')
    ap.add_argument('--native-service', dest='native_services', action='append', default=[],
                    help='Declare a new native service: '
                         'package.name.service')
    if get_bootstrap_name() != "service_only":
        ap.add_argument('--presplash', dest='presplash',
                        help=('A jpeg file to use as a screen while the '
                              'application is loading.'))
        ap.add_argument('--presplash-lottie', dest='presplash_lottie',
                        help=('A lottie (json) file to use as an animation while the '
                              'application is loading.'))
        ap.add_argument('--presplash-color',
                        dest='presplash_color',
                        default='#000000',
                        help=('A string to set the loading screen '
                              'background color. '
                              'Supported formats are: '
                              '#RRGGBB #AARRGGBB or color names '
                              'like red, green, blue, etc.'))
        ap.add_argument('--window', dest='window', action='store_true',
                        default=False,
                        help='Indicate if the application will be windowed')
        ap.add_argument('--manifest-orientation', dest='manifest_orientation',
                        help=('The orientation that will be set in the '
                              'android:screenOrientation attribute of the activity '
                              'in the AndroidManifest.xml file. If not set, '
                              'the value will be synthesized from the --orientation option.'))
        ap.add_argument('--orientation', dest='orientation',
                        action="append", default=[],
                        choices=['portrait', 'landscape', 'landscape-reverse', 'portrait-reverse'],
                        help=('The orientations that the app will display in. '
                              'Since Android ignores android:screenOrientation '
                              'when in multi-window mode (Which is the default on Android 12+), '
                              'this option will also set the window orientation hints '
                              'for apps using the (default) SDL bootstrap.'
                              'If multiple orientations are given, android:screenOrientation '
                              'will be set to "unspecified"'))

    ap.add_argument('--enable-androidx', dest='enable_androidx',
                    action='store_true',
                    help=('Enable the AndroidX support library, '
                          'requires api = 28 or greater'))
    ap.add_argument('--android-entrypoint', dest='android_entrypoint',
                    default=DEFAULT_PYTHON_ACTIVITY_JAVA_CLASS,
                    help='Defines which java class will be used for startup, usually a subclass of PythonActivity')
    ap.add_argument('--android-apptheme', dest='android_apptheme',
                    default='@android:style/Theme.NoTitleBar',
                    help='Defines which app theme should be selected for the main activity')
    ap.add_argument('--add-compile-option', dest='compile_options', default=[],
                    action='append', help='add compile options to gradle.build')
    ap.add_argument('--add-gradle-repository', dest='gradle_repositories',
                    default=[],
                    action='append',
                    help='Ddd a repository for gradle')
    ap.add_argument('--add-packaging-option', dest='packaging_options',
                    default=[],
                    action='append',
                    help='Dndroid packaging options')

    ap.add_argument('--wakelock', dest='wakelock', action='store_true',
                    help=('Indicate if the application needs the device '
                          'to stay on'))
    ap.add_argument('--blacklist', dest='blacklist',
                    default=join(curdir, 'blacklist.txt'),
                    help=('Use a blacklist file to match unwanted file in '
                          'the final APK'))
    ap.add_argument('--whitelist', dest='whitelist',
                    default=join(curdir, 'whitelist.txt'),
                    help=('Use a whitelist file to prevent blacklisting of '
                          'file in the final APK'))
    ap.add_argument('--release', dest='build_mode', action='store_const',
                    const='release', default='debug',
                    help='Build your app as a non-debug release build. '
                         '(Disables gdb debugging among other things)')
    ap.add_argument('--with-debug-symbols', dest='with_debug_symbols',
                    action='store_const', const=True, default=False,
                    help='Will keep debug symbols from `.so` files.')
    ap.add_argument('--add-jar', dest='add_jar', action='append',
                    help=('Add a Java .jar to the libs, so you can access its '
                          'classes with pyjnius. You can specify this '
                          'argument more than once to include multiple jars'))
    ap.add_argument('--add-aar', dest='add_aar', action='append',
                    help=('Add an aar dependency manually'))
    ap.add_argument('--depend', dest='depends', action='append',
                    help=('Add a external dependency '
                          '(eg: com.android.support:appcompat-v7:19.0.1)'))
    # The --sdk option has been removed, it is ignored in favour of
    # --android-api handled by toolchain.py
    ap.add_argument('--sdk', dest='sdk_version', default=-1,
                    type=int, help=('Deprecated argument, does nothing'))
    ap.add_argument('--minsdk', dest='min_sdk_version',
                    default=ndk_api, type=int,
                    help=('Minimum Android SDK version that the app supports. '
                          'Defaults to {}.'.format(ndk_api)))
    ap.add_argument('--allow-minsdk-ndkapi-mismatch', default=False,
                    action='store_true',
                    help=('Allow the --minsdk argument to be different from '
                          'the discovered ndk_api in the dist'))
    ap.add_argument('--intent-filters', dest='intent_filters',
                    help=('Add intent-filters xml rules to the '
                          'AndroidManifest.xml file. The argument is a '
                          'filename containing xml. The filename should be '
                          'located relative to the python-for-android '
                          'directory'))
    ap.add_argument('--res_xml', dest='res_xmls', action='append', default=[],
                    help='Add files to res/xml directory (for example device-filters)', nargs='+')
    ap.add_argument('--with-billing', dest='billing_pubkey',
                    help='If set, the billing service will be added (not implemented)')
    ap.add_argument('--add-source', dest='extra_source_dirs', action='append',
                    help='Include additional source dirs in Java build')
    if get_bootstrap_name() == "webview":
        ap.add_argument('--port',
                        help='The port on localhost that the WebView will access',
                        default='5000')
    ap.add_argument('--try-system-python-compile', dest='try_system_python_compile',
                    action='store_true',
                    help='Use the system python during compileall if possible.')
    ap.add_argument('--sign', action='store_true',
                    help=('Try to sign the APK with your credentials. You must set '
                          'the appropriate environment variables.'))
    ap.add_argument('--add-activity', dest='add_activity', action='append',
                    help='Add this Java class as an Activity to the manifest.')
    ap.add_argument('--activity-launch-mode',
                    dest='activity_launch_mode',
                    default='singleTask',
                    help='Set the launch mode of the main activity in the manifest.')
    ap.add_argument('--allow-backup', dest='allow_backup', default='true',
                    help="if set to 'false', then android won't backup the application.")
    ap.add_argument('--backup-rules', dest='backup_rules', default='',
                    help=('Backup rules for Android Auto Backup. Argument is a '
                          'filename containing xml. The filename should be '
                          'located relative to the private directory containing your source code '
                          'files (containing your main.py entrypoint). '
                          'See https://developer.android.com/guide/topics/data/'
                          'autobackup#IncludingFiles for more information'))
    ap.add_argument('--no-byte-compile-python', dest='byte_compile_python',
                    action='store_false', default=True,
                    help='Skip byte compile for .py files.')
    ap.add_argument('--no-optimize-python', dest='optimize_python',
                    action='store_false', default=True,
                    help=('Whether to compile to optimised .pyc files, using -OO '
                          '(strips docstrings and asserts)'))
    ap.add_argument('--extra-manifest-xml', default='',
                    help=('Extra xml to write directly inside the <manifest> element of'
                          'AndroidManifest.xml'))
    ap.add_argument('--extra-manifest-application-arguments', default='',
                    help='Extra arguments to be added to the <manifest><application> tag of'
                         'AndroidManifest.xml')
    ap.add_argument('--manifest-placeholders', dest='manifest_placeholders',
                    default='[:]', help=('Inject build variables into the manifest '
                                         'via the manifestPlaceholders property'))
    ap.add_argument('--service-class-name', dest='service_class_name', default=DEFAULT_PYTHON_SERVICE_JAVA_CLASS,
                    help='Use that parameter if you need to implement your own PythonServive Java class')
    ap.add_argument('--activity-class-name', dest='activity_class_name', default=DEFAULT_PYTHON_ACTIVITY_JAVA_CLASS,
                    help='The full java class name of the main activity')
    if get_bootstrap_name() == "qt":
        ap.add_argument('--qt-libs', dest='qt_libs', required=True,
                        help='comma separated list of Qt libraries to be loaded')
        ap.add_argument('--load-local-libs', dest='load_local_libs', required=True,
                        help='comma separated list of Qt plugin libraries to be loaded')
        ap.add_argument('--init-classes', dest='init_classes', default='',
                        help='comma separated list of java class names to be loaded from the Qt jar files, '
                             'specified through add_jar cli option')

    return ap


def parse_args_and_make_package(args=None):
    global BLACKLIST_PATTERNS, WHITELIST_PATTERNS, PYTHON

    ndk_api = get_dist_ndk_min_api_level()
    ap = create_argument_parser()

    # Put together arguments, and add those from .p4a config file:
    if args is None:
        args = sys.argv[1:]

    def _read_configuration():
        if not exists(".p4a"):
            return
        print("Reading .p4a configuration")
        with open(".p4a") as fd:
            lines = fd.readlines()
        lines = [shlex.split(line)
                 for line in lines if not line.startswith("#")]
        for line in lines:
            for arg in line:
                args.append(arg)
    _read_configuration()

    args = ap.parse_args(args)

    if args.name and args.name[0] == '"' and args.name[-1] == '"':
        args.name = args.name[1:-1]

    if ndk_api != args.min_sdk_version:
        print(('WARNING: --minsdk argument does not match the api that is '
               'compiled against. Only proceed if you know what you are '
               'doing, otherwise use --minsdk={} or recompile against api '
               '{}').format(ndk_api, args.min_sdk_version))
        if not args.allow_minsdk_ndkapi_mismatch:
            print('You must pass --allow-minsdk-ndkapi-mismatch to build '
                  'with --minsdk different to the target NDK api from the '
                  'build step')
            sys.exit(1)
        else:
            print('Proceeding with --minsdk not matching build target api')

    if args.billing_pubkey:
        print('Billing not yet supported!')
        sys.exit(1)

    if args.sdk_version != -1:
        print('WARNING: Received a --sdk argument, but this argument is '
              'deprecated and does nothing.')
        args.sdk_version = -1  # ensure it is not used

    args.permissions = parse_permissions(args.permissions)

    args.manifest_orientation = get_manifest_orientation(
        args.orientation, args.manifest_orientation
    )

    if get_bootstrap_name() == "sdl2":
        args.sdl_orientation_hint = get_sdl_orientation_hint(args.orientation)

    if args.res_xmls and isinstance(args.res_xmls[0], list):
        args.res_xmls = [x for res in args.res_xmls for x in res]

    if args.try_system_python_compile:
        # Hardcoding python2.7 is okay for now, as python3 skips the
        # compilation anyway
        python_executable = 'python2.7'
        try:
            subprocess.call([python_executable, '--version'])
        except (OSError, subprocess.CalledProcessError):
            pass
        else:
            PYTHON = python_executable

    if args.blacklist:
        with open(args.blacklist) as fd:
            patterns = [x.strip() for x in fd.read().splitlines()
                        if x.strip() and not x.strip().startswith('#')]
        BLACKLIST_PATTERNS += patterns

    if args.whitelist:
        with open(args.whitelist) as fd:
            patterns = [x.strip() for x in fd.read().splitlines()
                        if x.strip() and not x.strip().startswith('#')]
        WHITELIST_PATTERNS += patterns

    if args.private is None and \
            get_bootstrap_name() == 'sdl2' and args.launcher is None:
        print('Need --private directory or ' +
              '--launcher (SDL2 bootstrap only)' +
              'to have something to launch inside the .apk!')
        sys.exit(1)
    make_package(args)

    return args


if __name__ == "__main__":
    parse_args_and_make_package()
