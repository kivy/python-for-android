#!/usr/bin/env python2.7

from __future__ import print_function

from os.path import dirname, join, isfile, realpath, relpath, split, exists
from os import makedirs
import os
import tarfile
import time
import subprocess
import shutil
from zipfile import ZipFile
import sys
import re
import shlex

from fnmatch import fnmatch

import jinja2

if os.name == 'nt':
    ANDROID = 'android.bat'
    ANT = 'ant.bat'
else:
    ANDROID = 'android'
    ANT = 'ant'

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
    # '*.py',

    # temp files
    '~',
    '*.bak',
    '*.swp',
]

WHITELIST_PATTERNS = []

python_files = []


environment = jinja2.Environment(loader=jinja2.FileSystemLoader(
    join(curdir, 'templates')))

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

def make_python_zip():
    '''
    Search for all the python related files, and construct the pythonXX.zip
    According to
    # http://randomsplat.com/id5-cross-compiling-python-for-embedded-linux.html
    site-packages, config and lib-dynload will be not included.
    '''

    if not exists('private'):
        print('No compiled python is present to zip, skipping.')
        print('this should only be the case if you are using the CrystaX python')
        return

    global python_files
    d = realpath(join('private', 'lib', 'python2.7'))


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
#        print('%s: %s' % (tfn, fn))
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


def compile_dir(dfn):
    '''
    Compile *.py in directory `dfn` to *.pyo
    '''

    return  # Currently leaving out the compile to pyo step because it's somehow broken
    # -OO = strip docstrings
    subprocess.call([PYTHON, '-OO', '-m', 'compileall', '-f', dfn])


def make_package(args):
    # # Update the project to a recent version.
    # try:
    #     subprocess.call([ANDROID, 'update', 'project', '-p', '.', '-t',
    #                      'android-{}'.format(args.sdk_version)])
    # except (OSError, IOError):
    #     print('An error occured while calling', ANDROID, 'update')
    #     print('Your PATH must include android tools.')
    #     sys.exit(-1)

    # Delete the old assets.
    if exists('assets/public.mp3'):
        os.unlink('assets/public.mp3')

    if exists('assets/private.mp3'):
        os.unlink('assets/private.mp3')

    # In order to speedup import and initial depack,
    # construct a python27.zip
    make_python_zip()

    # Package up the private data (public not supported).
    tar_dirs = [args.private]
    if exists('private'):
        tar_dirs.append('private')
    if exists('crystax_python'):
        tar_dirs.append('crystax_python')
    if args.private:
        make_tar('assets/private.mp3', tar_dirs, args.ignore_path)
    # else:
    #     make_tar('assets/private.mp3', ['private'])

    # if args.dir:
    #     make_tar('assets/public.mp3', [args.dir], args.ignore_path)


    # # Build.
    # try:
    #     for arg in args.command:
    #         subprocess.check_call([ANT, arg])
    # except (OSError, IOError):
    #     print 'An error occured while calling', ANT
    #     print 'Did you install ant on your system ?'
    #     sys.exit(-1)


    # Prepare some variables for templating process

#     default_icon = 'templates/kivy-icon.png'
#     shutil.copy(args.icon or default_icon, 'res/drawable/icon.png')

#     default_presplash = 'templates/kivy-presplash.jpg'
#     shutil.copy(args.presplash or default_presplash,
#                 'res/drawable/presplash.jpg')

    # If extra Java jars were requested, copy them into the libs directory
    if args.add_jar:
        for jarname in args.add_jar:
            if not exists(jarname):
                print('Requested jar does not exist: {}'.format(jarname))
                sys.exit(-1)
            shutil.copy(jarname, 'libs')

#     versioned_name = (args.name.replace(' ', '').replace('\'', '') +
#                       '-' + args.version)

#     version_code = 0
#     if not args.numeric_version:
#         for i in args.version.split('.'):
#             version_code *= 100
#             version_code += int(i)
#         args.numeric_version = str(version_code)

#     if args.intent_filters:
#         with open(args.intent_filters) as fd:
#             args.intent_filters = fd.read()

    if args.extra_source_dirs:
        esd = []
        for spec in args.extra_source_dirs:
            if ':' in spec:
                specdir, specincludes = spec.split(':')
            else:
                specdir = spec
                specincludes = '**'
            esd.append((realpath(specdir), specincludes))
        args.extra_source_dirs = esd
    else:
        args.extra_source_dirs = []

    service = False
    service_main = join(realpath(args.private), 'service', 'main.py')
    if exists(service_main) or exists(service_main + 'o'):
        service = True

    service_names = []
    for sid, spec in enumerate(args.services):
        spec = spec.split(':')
        name = spec[0]
        entrypoint = spec[1]
        options = spec[2:]

        foreground = 'foreground' in options
        sticky = 'sticky' in options

        service_names.append(name)
        render(
            'Service.tmpl.java',
            'src/{}/Service{}.java'.format(args.package.replace(".", "/"), name.capitalize()),
            name=name,
            entrypoint=entrypoint,
            args=args,
            foreground=foreground,
            sticky=sticky,
            service_id=sid + 1,
        )

    render(
        'AndroidManifest.tmpl.xml',
        'AndroidManifest.xml',
        args=args,
        service=service,
        service_names=service_names,
        )

    render(
        'app.build.tmpl.gradle',
        'app.build.gradle',
        args=args
        )

#     render(
#         'build.tmpl.xml',
#         'build.xml',
#         args=args,
#         versioned_name=versioned_name)

#     render(
#         'strings.tmpl.xml',
#         'res/values/strings.xml',
#         args=args)

#     render(
#         'custom_rules.tmpl.xml',
#         'custom_rules.xml',
#         args=args)

#     with open(join(dirname(__file__), 'res',
#                    'values', 'strings.xml')) as fileh:
#         lines = fileh.read()

#     with open(join(dirname(__file__), 'res',
#                    'values', 'strings.xml'), 'w') as fileh:
#         fileh.write(re.sub(r'"private_version">[0-9\.]*<',
#                            '"private_version">{}<'.format(
#                                str(time.time())), lines))


def parse_args(args=None):

    global BLACKLIST_PATTERNS, WHITELIST_PATTERNS
    default_android_api = 12
    import argparse
    ap = argparse.ArgumentParser(description='''\
Package a Python application for Android.

For this to work, Java and Ant need to be in your path, as does the
tools directory of the Android SDK.
''')

    ap.add_argument('--private', dest='private',
                    help='the dir of user files',
                    required=True)
    ap.add_argument('--package', dest='package',
                    help=('The name of the java package the project will be'
                          ' packaged under.'),
                    required=True)
#     ap.add_argument('--name', dest='name',
#                     help=('The human-readable name of the project.'),
#                     required=True)
#     ap.add_argument('--numeric-version', dest='numeric_version',
#                     help=('The numeric version number of the project. If not '
#                           'given, this is automatically computed from the '
#                           'version.'))
#     ap.add_argument('--version', dest='version',
#                     help=('The version number of the project. This should '
#                           'consist of numbers and dots, and should have the '
#                           'same number of groups of numbers as previous '
#                           'versions.'),
#                     required=True)
#     ap.add_argument('--orientation', dest='orientation', default='portrait',
#                     help=('The orientation that the game will display in. '
#                           'Usually one of "landscape", "portrait" or '
#                           '"sensor"'))
#     ap.add_argument('--icon', dest='icon',
#                     help='A png file to use as the icon for the application.')
#     ap.add_argument('--permission', dest='permissions', action='append',
#                     help='The permissions to give this app.')
    ap.add_argument('--meta-data', dest='meta_data', action='append',
                    help='Custom key=value to add in application metadata')
#     ap.add_argument('--presplash', dest='presplash',
#                     help=('A jpeg file to use as a screen while the '
#                           'application is loading.'))
    ap.add_argument('--wakelock', dest='wakelock', action='store_true',
                    help=('Indicate if the application needs the device '
                          'to stay on'))
    ap.add_argument('--window', dest='window', action='store_false',
                    help='Indicate if the application will be windowed')
    ap.add_argument('--blacklist', dest='blacklist',
                    default=join(curdir, 'blacklist.txt'),
                    help=('Use a blacklist file to match unwanted file in '
                          'the final APK'))
    ap.add_argument('--whitelist', dest='whitelist',
                    default=join(curdir, 'whitelist.txt'),
                    help=('Use a whitelist file to prevent blacklisting of '
                          'file in the final APK'))
    ap.add_argument('--add-jar', dest='add_jar', action='append',
                    help=('Add a Java .jar to the libs, so you can access its '
                          'classes with pyjnius. You can specify this '
                          'argument more than once to include multiple jars'))
    ap.add_argument('--sdk', dest='sdk_version', default=-1,
                    type=int, help=('Android SDK version to use. Default to '
                                    'the value of minsdk'))
    ap.add_argument('--minsdk', dest='min_sdk_version',
                    default=default_android_api, type=int,
                    help=('Minimum Android SDK version to use. Default to '
                          'the value of ANDROIDAPI, or {} if not set'
                          .format(default_android_api)))
#     ap.add_argument('--intent-filters', dest='intent_filters',
#                     help=('Add intent-filters xml rules to the '
#                           'AndroidManifest.xml file. The argument is a '
#                           'filename containing xml. The filename should be '
#                           'located relative to the python-for-android '
#                           'directory'))
#     ap.add_argument('--with-billing', dest='billing_pubkey',
#                     help='If set, the billing service will be added (not implemented)')
    ap.add_argument('--service', dest='services', action='append',
                    help='Declare a new service entrypoint: '
                         'NAME:PATH_TO_PY[:foreground]')
    ap.add_argument('--add-source', dest='extra_source_dirs', action='append',
                    help='Include additional source dirs in Java build')

    def _read_configuration():
        # search for a .p4a configuration file in the current directory
        if not exists(".p4a"):
            return
        print("Reading .p4a configuration")
        with open(".p4a") as fd:
            lines = fd.readlines()
        lines = [shlex.split(line)
                 for line in lines if not line.startswith("#")]
        for line in lines:
            for arg in line:
                sys.argv.append(arg)

    _read_configuration()

    if args is None:
        args = sys.argv[1:]
    args = ap.parse_args(args)
    args.ignore_path = []

#     if args.billing_pubkey:
#         print('Billing not yet supported in sdl2 bootstrap!')
#         exit(1)

    if args.sdk_version == -1:
        args.sdk_version = args.min_sdk_version

#     if args.permissions is None:
#         args.permissions = []

    if args.meta_data is None:
        args.meta_data = []

    if args.services is None:
        args.services = []

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

    make_package(args)

    return args


if __name__ == "__main__":

    parse_args()
