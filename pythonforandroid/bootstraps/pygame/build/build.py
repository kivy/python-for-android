#!/usr/bin/env python2.7

from os.path import dirname, join, isfile, realpath, relpath, split, exists
from zipfile import ZipFile
import sys
sys.path.insert(0, 'buildlib/jinja2.egg')
sys.path.insert(0, 'buildlib')

from fnmatch import fnmatch
import tarfile
import os
import shutil
import subprocess
import time
import jinja2

# The extension of the android and ant commands.
if os.name == 'nt':
    ANDROID = 'android.bat'
    ANT = 'ant.bat'
else:
    ANDROID = 'android'
    ANT = 'ant'

# if ANDROIDSDK is on path, use android from this path
ANDROIDSDK = os.environ.get('ANDROIDSDK')
if ANDROIDSDK:
    ANDROID = os.path.join(ANDROIDSDK, 'tools', ANDROID)

curdir = dirname(__file__)

# Try to find a host version of Python that matches our ARM version.
PYTHON = join(curdir, 'python-install', 'bin', 'python.host')

BLACKLIST_PATTERNS = [
    # code versionning
    '^*.hg/*',
    '^*.git/*',
    '^*.bzr/*',
    '^*.svn/*',

    # pyc/py
    '*.pyc',
    '*.py',

    # temp files
    '~',
    '*.bak',
    '*.swp',
]

WHITELIST_PATTERNS = []

python_files = []


# Used by render.
environment = jinja2.Environment(loader=jinja2.FileSystemLoader(
    join(curdir, 'templates')))


def render(template, dest, **kwargs):
    '''Using jinja2, render `template` to the filename `dest`, supplying the

    keyword arguments as template parameters.
    '''

    template = environment.get_template(template)
    text = template.render(**kwargs)

    f = open(dest, 'wb')
    f.write(text.encode('utf-8'))
    f.close()


def compile_dir(dfn):
    '''
    Compile *.py in directory `dfn` to *.pyo
    '''

    # -OO = strip docstrings
    subprocess.call([PYTHON, '-OO', '-m', 'compileall', '-f', dfn])


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
            subdirlist.append(os.path.join(basedir, item))
    for subdir in subdirlist:
        for fn in listfiles(subdir):
            yield fn


def make_pythonzip():
    '''
    Search for all the python related files, and construct the pythonXX.zip
    According to
    # http://randomsplat.com/id5-cross-compiling-python-for-embedded-linux.html
    site-packages, config and lib-dynload will be not included.
    '''
    global python_files
    d = realpath(join('private', 'lib', 'python2.7'))

    # selector function
    def select(fn):
        if is_blacklist(fn):
            return False
        fn = realpath(fn)
        assert(fn.startswith(d))
        fn = fn[len(d):]
        if (fn.startswith('/site-packages/') or
            fn.startswith('/config/') or
            fn.startswith('/lib-dynload/') or
            fn.startswith('/libpymodules.so')):
            return False
        return fn

    # get a list of all python file
    python_files = [x for x in listfiles(d) if select(x)]

    # create the final zipfile
    zfn = join('private', 'lib', 'python27.zip')
    zf = ZipFile(zfn, 'w')

    # put all the python files in it
    for fn in python_files:
        afn = fn[len(d):]
        zf.write(fn, afn)
    zf.close()


def make_tar(tfn, source_dirs, ignore_path=[]):
    '''
    Make a zip file `fn` from the contents of source_dis.
    '''

    # selector function
    def select(fn):
        rfn = realpath(fn)
        for p in ignore_path:
            if p.endswith('/'):
                p = p[:-1]
            if rfn.startswith(p):
                return False
        if rfn in python_files:
            return False
        return not is_blacklist(fn)

    # get the files and relpath file of all the directory we asked for
    files = []
    for sd in source_dirs:
        sd = realpath(sd)
        compile_dir(sd)
        files += [(x, relpath(realpath(x), sd)) for x in listfiles(sd)
                  if select(x)]

    # create tar.gz of thoses files
    tf = tarfile.open(tfn, 'w:gz', format=tarfile.USTAR_FORMAT)
    dirs = []
    for fn, afn in files:
#         print('%s: %s' % (tfn, fn))
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
                tf.addfile(tinfo)

        # put the file
        tf.add(fn, afn)
    tf.close()


def make_package(args):
    version_code = 0
    manifest_extra = ['<uses-feature android:glEsVersion="0x00020000" />']
    for filename in args.manifest_extra:
        with open(filename, "r") as fd:
            content = fd.read()
            manifest_extra.append(content)
    manifest_extra = '\n'.join(manifest_extra)
    url_scheme = 'kivy'
    default_icon = 'templates/kivy-icon.png'
    default_presplash = 'templates/kivy-presplash.jpg'
    default_ouya_icon = 'templates/kivy-ouya-icon.png'
    # Figure out the version code, if necessary.
    if not args.numeric_version:
        for i in args.version.split('.'):
            version_code *= 100
            version_code += int(i)

        args.numeric_version = str(version_code)

    # args.name = args.name.decode('utf-8')
    # if args.icon_name:
    #     args.icon_name = args.icon_name.decode('utf-8')

    versioned_name = (args.name.replace(' ', '').replace('\'', '') +
                      '-' + args.version)

    # Android SDK rev14 needs two ant execs (ex: debug installd) and
    # new build.xml
    build_tpl = 'build.xml'

    if not args.icon_name:
        args.icon_name = args.name

    # Annoying fixups.
    args.name = args.name.replace('\'', '\\\'')
    args.icon_name = args.icon_name.replace('\'', '\\\'')

    # Figure out versions of the private and public data.
    private_version = str(time.time())

    if args.dir:
        public_version = private_version
    else:
        public_version = None

    if args.intent_filters:
        intent_filters = open(args.intent_filters).read()
    else:
        intent_filters = ''

    directory = args.dir if public_version else args.private
    # Ignore warning if the launcher is in args
    if not args.launcher:
        if not (exists(join(realpath(directory), 'main.py')) or
                exists(join(realpath(directory), 'main.pyo'))):
            print('''BUILD FAILURE: No main.py(o) found in your app directory.
This file must exist to act as the entry point for you app. If your app is
started by a file with a different name, rename it to main.py or add a
main.py that loads it.''')
            exit(1)

    # Figure out if application has service part
    service = False
    if directory:
        service_main = join(realpath(directory), 'service', 'main.py')
        if os.path.exists(service_main) or os.path.exists(service_main + 'o'):
            service = True

    # Check if OUYA support is enabled
    if args.ouya_category:
        args.ouya_category = args.ouya_category.upper()
        if args.ouya_category not in ('GAME', 'APP'):
            print('Invalid --ouya-category argument. should be one of'
                  'GAME or APP')
            sys.exit(-1)

    # Render the various templates into control files.
    render(
        'AndroidManifest.tmpl.xml',
        'AndroidManifest.xml',
        args=args,
        service=service,
        url_scheme=url_scheme,
        intent_filters=intent_filters,
        manifest_extra=manifest_extra,
        )

    render(
        'Configuration.tmpl.java',
        'src/org/renpy/android/Configuration.java',
        args=args)

    render(
        build_tpl,
        'build.xml',
        args=args,
        versioned_name=versioned_name)

    render(
        'strings.xml',
        'res/values/strings.xml',
        public_version=public_version,
        private_version=private_version,
        url_scheme=url_scheme,
        args=args)

    # Update the project to a recent version.
    try:
        subprocess.call([ANDROID, 'update', 'project', '-p', '.', '-t',
                         'android-{}'.format(args.sdk_version)])
    except (OSError, IOError):
        print('An error occured while calling', ANDROID, 'update')
        print('Your PATH must include android tools.')
        sys.exit(-1)

    # Delete the old assets.
    if os.path.exists('assets/public.mp3'):
        os.unlink('assets/public.mp3')

    if os.path.exists('assets/private.mp3'):
        os.unlink('assets/private.mp3')

    # In order to speedup import and initial depack,
    # construct a python27.zip
    make_pythonzip()

    # Package up the private and public data.
    if args.private:
        make_tar('assets/private.mp3', ['private', args.private], args.ignore_path)
    else:
        make_tar('assets/private.mp3', ['private'])

    if args.dir:
        make_tar('assets/public.mp3', [args.dir], args.ignore_path)

    # Copy over the icon and presplash files.
    shutil.copy(args.icon or default_icon, 'res/drawable/icon.png')
    shutil.copy(args.presplash or default_presplash,
                'res/drawable/presplash.jpg')

    # If OUYA support was requested, copy over the OUYA icon
    if args.ouya_category:
        if not os.path.isdir('res/drawable-xhdpi'):
            os.mkdir('res/drawable-xhdpi')
        shutil.copy(args.ouya_icon or default_ouya_icon,
                    'res/drawable-xhdpi/ouya_icon.png')

    # If extra Java jars were requested, copy them into the libs directory
    if args.add_jar:
        for jarname in args.add_jar:
            if not os.path.exists(jarname):
                print('Requested jar does not exist: {}'.format(jarname))
                sys.exit(-1)
            shutil.copy(jarname, 'libs')

    # Build.
    try:
        for arg in args.command:
            subprocess.check_call([ANT, arg])
    except (OSError, IOError):
        print('An error occured while calling', ANT)
        print('Did you install ant on your system ?')
        sys.exit(-1)

def parse_args(args=None):
    import argparse

    # get default SDK version from environment
    android_api = os.environ.get('ANDROIDAPI', 8)

    ap = argparse.ArgumentParser(description='''\
Package a Python application for Android.

For this to work, Java and Ant need to be in your path, as does the
tools directory of the Android SDK.
''')

    ap.add_argument('--package', dest='package',
                    help=('The name of the java package the project will be'
                          ' packaged under.'),
                    required=True)
    ap.add_argument('--name', dest='name',
                    help=('The human-readable name of the project.'),
                    required=True)
    ap.add_argument('--version', dest='version',
                    help=('The version number of the project. This should '
                          'consist of numbers and dots, and should have the '
                          'same number of groups of numbers as previous '
                          'versions.'),
                    required=True)
    ap.add_argument('--numeric-version', dest='numeric_version',
                    help=('The numeric version number of the project. If not '
                          'given, this is automatically computed from the '
                          'version.'))
    ap.add_argument('--dir', dest='dir',
                    help=('The directory containing public files for the '
                          'project.'))
    ap.add_argument('--private', dest='private',
                    help=('The directory containing additional private files '
                          'for the project.'))
    ap.add_argument('--launcher', dest='launcher', action='store_true',
                    help=('Provide this argument to build a multi-app '
                          'launcher, rather than a single app.'))
    ap.add_argument('--icon-name', dest='icon_name',
                    help='The name of the project\'s launcher icon.')
    ap.add_argument('--orientation', dest='orientation', default='landscape',
                    help=('The orientation that the game will display in. '
                          'Usually one of "landscape", "portrait" or '
                          '"sensor"'))
    ap.add_argument('--permission', dest='permissions', action='append',
                    help='The permissions to give this app.', nargs='+')
    ap.add_argument('--ignore-path', dest='ignore_path', action='append',
                    help='Ignore path when building the app')
    ap.add_argument('--icon', dest='icon',
                    help='A png file to use as the icon for the application.')
    ap.add_argument('--presplash', dest='presplash',
                    help=('A jpeg file to use as a screen while the '
                          'application is loading.'))
    ap.add_argument('--ouya-category', dest='ouya_category',
                    help=('Valid values are GAME and APP. This must be '
                          'specified to enable OUYA console support.'))
    ap.add_argument('--ouya-icon', dest='ouya_icon',
                    help=('A png file to use as the icon for the application '
                          'if it is installed on an OUYA console.'))
    ap.add_argument('--install-location', dest='install_location',
                    default='auto',
                    help=('The default install location. Should be "auto", '
                          '"preferExternal" or "internalOnly".'))
    ap.add_argument('--compile-pyo', dest='compile_pyo', action='store_true',
                    help=('Compile all .py files to .pyo, and only distribute '
                          'the compiled bytecode.'))
    ap.add_argument('--intent-filters', dest='intent_filters',
                    help=('Add intent-filters xml rules to the '
                          'AndroidManifest.xml file. The argument is a '
                          'filename containing xml. The filename should be '
                          'located relative to the python-for-android '
                          'directory'))
    ap.add_argument('--with-billing', dest='billing_pubkey',
                    help='If set, the billing service will be added')
    ap.add_argument('--blacklist', dest='blacklist',
                    default=join(curdir, 'blacklist.txt'),
                    help=('Use a blacklist file to match unwanted file in '
                          'the final APK'))
    ap.add_argument('--whitelist', dest='whitelist',
                    default=join(curdir, 'whitelist.txt'),
                    help=('Use a whitelist file to prevent blacklisting of '
                          'file in the final APK'))
    ap.add_argument('--sdk', dest='sdk_version', default=android_api,
                    help='Android SDK version to use. Default to 8')
    ap.add_argument('--minsdk', dest='min_sdk_version', default=android_api,
                    type=int,
                    help='Minimum Android SDK version to use. Default to 8')
    ap.add_argument('--window', dest='window', action='store_true',
                    help='Indicate if the application will be windowed')
    ap.add_argument('--wakelock', dest='wakelock', action='store_true',
                    help=('Indicate if the application needs the device '
                          'to stay on'))
    ap.add_argument('command', nargs='*',
                    help=('The command to pass to ant (debug, release, '
                          'installd, installr)'))
    ap.add_argument('--add-jar', dest='add_jar', action='append',
                    help=('Add a Java .jar to the libs, so you can access its '
                          'classes with pyjnius. You can specify this '
                          'argument more than once to include multiple jars'))
    ap.add_argument('--meta-data', dest='meta_data', action='append',
                    help='Custom key=value to add in application metadata')
    ap.add_argument('--resource', dest='resource', action='append',
                    help='Custom key=value to add in strings.xml resource file')
    ap.add_argument('--manifest-extra', dest='manifest_extra', action='append',
                    help='Custom file to add at the end of the manifest')

    if args is None:
        args = sys.argv[1:]
    args = ap.parse_args(args)

    if args.name and args.name[0] == '"' and args.name[-1] == '"':
        args.name = args.name[1:-1]

    if not args.dir and not args.private and not args.launcher:
        ap.error('One of --dir, --private, or --launcher must be supplied.')

    if args.permissions is None:
        args.permissions = []
    elif args.permissions:
        if isinstance(args.permissions[0], list):
            args.permissions = [p for perm in args.permissions for p in perm]

    if args.ignore_path is None:
        args.ignore_path = []

    if args.meta_data is None:
        args.meta_data = []

    if args.resource is None:
        args.resource = []

    if args.manifest_extra is None:
        args.manifest_extra = []

    if args.compile_pyo:
        if PYTHON is None:
            ap.error('To use --compile-pyo, you need Python 2.7.1 installed '
                     'and in your PATH.')
        global BLACKLIST_PATTERNS
        BLACKLIST_PATTERNS += ['*.py', '*.pyc']

    if args.blacklist:
        with open(args.blacklist) as fd:
            patterns = [x.strip() for x in fd.read().splitlines() if x.strip()
                        and not x.startswith('#')]
        BLACKLIST_PATTERNS += patterns

    if args.whitelist:
        with open(args.whitelist) as fd:
            patterns = [x.strip() for x in fd.read().splitlines() if x.strip()
                        and not x.startswith('#')]
        global WHITELIST_PATTERNS
        WHITELIST_PATTERNS += patterns

    make_package(args)

    return args


if __name__ == '__main__':
    parse_args()
