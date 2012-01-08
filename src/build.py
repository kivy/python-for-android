#!/usr/bin/python

from os.path import dirname, join
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

curdir = dirname(__file__)

# Try to find a host version of Python that matches our ARM version.
PYTHON = join(curdir, 'python-install', 'bin', 'python.host')

BLACKLIST_PATTERNS = [
    # code versionning
    '.hg',
    '.git',
    '.bzr',
    '.svn',

    # temp files
    '~',
    '.bak',
    '.swp',
]

# Used by render.
environment = jinja2.Environment(loader=jinja2.FileSystemLoader(
    join(curdir, 'templates')))

def render(template, dest, **kwargs):
    '''
    Using jinja2, render `template` to the filename `dest`, supplying the keyword
    arguments as template parameters.
    '''

    template = environment.get_template(template)
    text = template.render(**kwargs)

    f = file(dest, 'wb')
    f.write(text.encode('utf-8'))
    f.close()

def compile_dir(dfn):
    '''
    Compile *.py in directory `dfn` to *.pyo
    '''

    # -OO = strip docstrings
    subprocess.call([PYTHON,'-OO','-m','compileall','-f',dfn])

def is_blacklist(name):
    for pattern in BLACKLIST_PATTERNS:
        if fnmatch(name, '*/' + pattern):
            return True

def make_tar(fn, source_dirs, ignore_path=[]):
    '''
    Make a zip file `fn` from the contents of source_dis.
    '''

    tf = tarfile.open(fn, 'w:gz')

    for sd in source_dirs:
        compile_dir(sd)

        sd = os.path.abspath(sd)

        for dir, dirs, files in os.walk(sd):
            dirs = [d for d in dirs if not is_blacklist(d)]

            ignore = False
            for ip in ignore_path:
                if dir.startswith(ip):
                    ignore = True
            if ignore:
                print 'ignored', fn
                continue

            for fn in dirs:
                fn = os.path.join(dir, fn)
                relfn = os.path.relpath(fn, sd)
                tf.add(fn, relfn, recursive=False)

            for fn in files:
                fn = os.path.join(dir, fn)
                relfn = os.path.relpath(fn, sd)
                if is_blacklist(relfn):
                    continue
                tf.add(fn, relfn)
                print 'add', fn

    # TODO: Fix me.
    # tf.writestr('.nomedia', '')
    tf.close()


def make_package(args):
    version_code = 0
    manifest_extra = '<uses-feature android:glEsVersion="0x00020000" />'
    url_scheme = 'kivy'
    default_icon = 'templates/kivy-icon.png'
    default_presplash = 'templates/kivy-presplash.jpg'
    # Figure out the version code, if necessary.
    if not args.numeric_version:
        for i in args.version.split('.'):
            version_code *= 100
            version_code += int(i)

        args.numeric_version = str(version_code)

    versioned_name = args.name.replace(' ', '').replace('\'', '') + '-' + args.version

    # Android SDK rev14 needs two ant execs (ex: debug installd) and new build.xml
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

    # Render the various templates into control files.
    render(
        'AndroidManifest.tmpl.xml',
        'AndroidManifest.xml',
        args = args,
        url_scheme = url_scheme,
        manifest_extra = manifest_extra,
        )

    render(
        build_tpl,
        'build.xml',
        args = args,
        versioned_name = versioned_name)

    render(
        'strings.xml',
        'res/values/strings.xml',
        public_version = public_version,
        private_version = private_version,
        url_scheme = url_scheme,
        args=args)

    # Update the project to a recent version.
    subprocess.call([ANDROID, 'update', 'project', '-p', '.', '-t', 'android-8'])

    # Delete the old assets.
    if os.path.exists('assets/public.mp3'):
        os.unlink('assets/public.mp3')

    if os.path.exists('assets/private.mp3'):
        os.unlink('assets/private.mp3')


    # Package up the private and public data.
    if args.private:
        make_tar('assets/private.mp3', [ 'private', args.private ])
    else:
        make_tar('assets/private.mp3', [ 'private' ])

    if args.dir:
        make_tar('assets/public.mp3', [ args.dir ], args.ignore_path)

    # Copy over the icon and presplash files.
    shutil.copy(args.icon or default_icon, 'res/drawable/icon.png')
    shutil.copy(args.presplash or default_presplash, 'res/drawable/presplash.jpg')

    # Build.
    map(lambda arg: subprocess.call([ANT, arg]), args.command)

if __name__ == '__main__':
    import argparse

    ap = argparse.ArgumentParser(description='''\
Package a Python application for Android.

For this to work, Java and Ant need to be in your path, as does the
tools directory of the Android SDK.
''')

    ap.add_argument('--package', dest='package', help='The name of the java package the project will be packaged under.', required=True)
    ap.add_argument('--name', dest='name', help='The human-readable name of the project.', required=True)
    ap.add_argument('--version', dest='version', help='The version number of the project. This should consist of numbers and dots, and should have the same number of groups of numbers as previous versions.', required=True)
    ap.add_argument('--numeric-version', dest='numeric_version', help='The numeric version number of the project. If not given, this is automatically computed from the version.')
    ap.add_argument('--dir', dest='dir', help='The directory containing public files for the project.')
    ap.add_argument('--private', dest='private', help='The directory containing additional private files for the project.')
    ap.add_argument('--launcher', dest='launcher', action='store_true',
            help='Provide this argument to build a multi-app launcher, rather than a single app.')
    ap.add_argument('--icon-name', dest='icon_name', help='The name of the project\'s launcher icon.')
    ap.add_argument('--orientation', dest='orientation', default='landscape', help='The orientation that the game will display in. Usually one of "landscape" or "portrait".')
    ap.add_argument('--permission', dest='permissions', action='append', help='The permissions to give this app.')
    ap.add_argument('--ignore-path', dest='ignore_path', action='append', help='Ignore path when building the app')
    ap.add_argument('--icon', dest='icon', help='A png file to use as the icon for the application.')
    ap.add_argument('--presplash', dest='presplash', help='A jpeg file to use as a screen while the application is loading.')
    ap.add_argument('--install-location', dest='install_location', default='auto', help='The default install location. Should be "auto", "preferExternal" or "internalOnly".')
    ap.add_argument('--compile-pyo', dest='compile_pyo', action='store_true', help='Compile all .py files to .pyo, and only distribute the compiled bytecode.')
    ap.add_argument('--blacklist', dest='blacklist',
        default=join(curdir, 'blacklist.txt'),
        help='Use a blacklist file to match unwanted file in the final APK')
    ap.add_argument('command', nargs='*', help='The command to pass to ant (debug, release, installd, installr)')

    args = ap.parse_args()

    if not args.dir and not args.private and not args.launcher:
        ap.error('One of --dir, --private, or --launcher must be supplied.')

    if args.permissions is None:
        args.permissions = [ ]

    if args.ignore_path is None:
        args.ignore_path = [ ]

    if args.compile_pyo:
        if PYTHON is None:
            ap.error('To use --compile-pyo, you need Python 2.7.1 installed and in your PATH.')
        BLACKLIST_PATTERNS += ['*.py', '*.pyc']

    if args.blacklist:
        with open(args.blacklist) as fd:
            patterns = [x.strip() for x in fd.read().splitlines() if x.strip() or
                    x.startswith('#')]
        BLACKLIST_PATTERNS += patterns

    make_package(args)

