#!/usr/bin/env python2.7

from __future__ import print_function

from os.path import dirname, join, isfile, realpath, relpath, split
import os
import tarfile
import time
import subprocess
import shutil
from zipfile import ZipFile
import sys
import re

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
    # '*.py',  # AND: Need to fix this to add it back

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

    template = environment.get_template(template)
    text = template.render(**kwargs)

    f = file(dest, 'wb')
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
            subdirlist.append(os.path.join(basedir, item))
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
        print('%s: %s' % (tfn, fn))
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

    return  # AND: Currently leaving out the compile to pyo step because it's somehow broken
    # -OO = strip docstrings
    subprocess.call([PYTHON, '-OO', '-m', 'compileall', '-f', dfn])


def make_package(args):
    url_scheme = 'kivy'

    # Figure out versions of the private and public data.
    private_version = str(time.time())

    # # Update the project to a recent version.
    # try:
    #     subprocess.call([ANDROID, 'update', 'project', '-p', '.', '-t',
    #                      'android-{}'.format(args.sdk_version)])
    # except (OSError, IOError):
    #     print('An error occured while calling', ANDROID, 'update')
    #     print('Your PATH must include android tools.')
    #     sys.exit(-1)

    # Delete the old assets.
    if os.path.exists('assets/public.mp3'):
        os.unlink('assets/public.mp3')

    if os.path.exists('assets/private.mp3'):
        os.unlink('assets/private.mp3')

    # In order to speedup import and initial depack,
    # construct a python27.zip
    make_python_zip()

    # Package up the private and public data.
    # AND: Just private for now
    if args.private:
        make_tar('assets/private.mp3', ['private', args.private], args.ignore_path)
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

    default_icon = 'templates/kivy-icon.png'
    shutil.copy(args.icon or default_icon, 'res/drawable/icon.png')
    
    versioned_name = (args.name.replace(' ', '').replace('\'', '') +
                      '-' + args.version)

    version_code = 0
    if not args.numeric_version:
        for i in args.version.split('.'):
            version_code *= 100
            version_code += int(i)
        args.numeric_version = str(version_code)

    render(
        'AndroidManifest.xml.tmpl',
        'AndroidManifest.xml',
        args=args,
        )

    render(
        'build.xml.tmpl',
        'build.xml',
        args=args,
        versioned_name=versioned_name)

    render(
        'strings.xml.tmpl',
        'res/values/strings.xml',
        args=args)

    with open(join(dirname(__file__), 'res',
                   'values', 'strings.xml')) as fileh:
        lines = fileh.read()

    with open(join(dirname(__file__), 'res',
                   'values', 'strings.xml'), 'w') as fileh:
        fileh.write(re.sub(r'"private_version">[0-9\.]*<',
                           '"private_version">{}<'.format(
                               str(time.time())), lines))
              

def parse_args(args=None):
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
    ap.add_argument('--orientation', dest='orientation', default='portrait',
                    help=('The orientation that the game will display in. '
                          'Usually one of "landscape", "portrait" or '
                          '"sensor"'))
    ap.add_argument('--icon', dest='icon',
                    help='A png file to use as the icon for the application.')

    if args is None:
        args = ap.parse_args()
    args.ignore_path = []

    make_package(args)

if __name__ == "__main__":

    parse_args()
