#!/usr/bin/env python
"""
Tool for compiling Android toolchain
====================================

This tool intend to replace all the previous tools/ in shell script.
"""

from __future__ import print_function

import sys
from sys import stdout
from os.path import join, dirname, realpath, exists, isdir, basename
from os import listdir, unlink, makedirs, environ, chdir, getcwd, walk, uname
import zipfile
import tarfile
import importlib
import io
import json
import glob
import shutil
import fnmatch
import re
from datetime import datetime
from distutils.spawn import find_executable
try:
    from urllib.request import FancyURLopener
except ImportError:
    from urllib import FancyURLopener

import requests
from appdirs import user_data_dir

curdir = dirname(__file__)
sys.path.insert(0, join(curdir, "tools", "external"))

import sh
import logging
import contextlib

from colorama import Style, Fore


logger = logging.getLogger('p4a')
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(stdout)
formatter = logging.Formatter('{}[%(levelname)s]{}: %(message)s'.format(
    Style.BRIGHT, Style.RESET_ALL))
ch.setFormatter(formatter)
logger.addHandler(ch)
# logger.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
info = logger.info
debug = logger.debug
warning = logger.warning



IS_PY3 = sys.version_info[0] >= 3

def info_main(*args):
    logger.info(''.join([Style.BRIGHT, Fore.GREEN] + list(args) +
                        [Style.RESET_ALL, Fore.RESET]))

def shprint(command, *args, **kwargs):
    kwargs["_iter"] = True
    kwargs["_out_bufsize"] = 1
    kwargs["_err_to_out"] = True
    if len(logger.handlers) > 1:
        logger.removeHandler(logger.handlers[1])
    command_path = str(command).split('/')
    command_string = command_path[-1]
    # if len(command_path) > 1:
    #     command_string = '.../' + command_string
    string = ' '.join(['running', Style.DIM, command_string] + list(args))
    short_string = string
    if len(string) > 100:
        short_string = string[:100] + '... (and {} more)'.format(len(string) - 100)
    logger.info(short_string + Style.RESET_ALL)
    logger.debug(string + Style.RESET_ALL)
    output = command(*args, **kwargs)
    for line in output:
        logger.debug(''.join([Style.DIM, '\t', line.rstrip()]))
    return output

# shprint(sh.ls, '-lah')
# exit(1)


def get_directory(filename):
    if filename.endswith('.tar.gz'):
        return basename(filename[:-7])
    elif filename.endswith('.tgz'):
        return basename(filename[:-4])
    elif filename.endswith('.tar.bz2'):
        return basename(filename[:-8])
    elif filename.endswith('.tbz2'):
        return basename(filename[:-5])
    elif filename.endswith('.zip'):
        return basename(filename[:-4])
    print('Unknown file extension for {}'.format(filename))
    exit(1)

def which(program, path_env):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in path_env.split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
    
    
@contextlib.contextmanager
def current_directory(new_dir):
    cur_dir = getcwd()
    logger.info(''.join((Fore.CYAN, '-> directory context ', new_dir,
                         Fore.RESET)))
    chdir(new_dir)
    yield
    logger.info(''.join((Fore.CYAN, '<- directory context ', cur_dir,
                         Fore.RESET)))
    chdir(cur_dir)
          


def cache_execution(f):
    def _cache_execution(self, *args, **kwargs):
        state = self.ctx.state
        key = "{}.{}".format(self.name, f.__name__)
        force = kwargs.pop("force", False)
        if args:
            for arg in args:
                key += ".{}".format(arg)
        key_time = "{}.at".format(key)
        if key in state and not force:
            print("# (ignored) {} {}".format(f.__name__.capitalize(), self.name))
            return
        print("{} {}".format(f.__name__.capitalize(), self.name))
        f(self, *args, **kwargs)
        state[key] = True
        state[key_time] = str(datetime.utcnow())
    return _cache_execution


class ChromeDownloader(FancyURLopener):
    version = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36')

urlretrieve = ChromeDownloader().retrieve


class JsonStore(object):
    """Replacement of shelve using json, needed for support python 2 and 3.
    """

    def __init__(self, filename):
        super(JsonStore, self).__init__()
        self.filename = filename
        self.data = {}
        if exists(filename):
            try:
                with io.open(filename, encoding='utf-8') as fd:
                    self.data = json.load(fd)
            except ValueError:
                print("Unable to read the state.db, content will be replaced.")

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.sync()

    def __delitem__(self, key):
        del self.data[key]
        self.sync()

    def __contains__(self, item):
        return item in self.data

    def get(self, item, default=None):
        return self.data.get(item, default)

    def keys(self):
        return self.data.keys()

    def remove_all(self, prefix):
        for key in self.data.keys()[:]:
            if not key.startswith(prefix):
                continue
            del self.data[key]
        self.sync()

    def sync(self):
        # http://stackoverflow.com/questions/12309269/write-json-data-to-file-in-python/14870531#14870531
        if IS_PY3:
            with open(self.filename, 'w') as fd:
                json.dump(self.data, fd, ensure_ascii=False)
        else:
            with io.open(self.filename, 'w', encoding='utf-8') as fd:
                fd.write(unicode(json.dumps(self.data, ensure_ascii=False)))

class Arch(object):
    def __init__(self, ctx):
        super(Arch, self).__init__()
        self.ctx = ctx

    def __str__(self):
        return self.arch

    @property
    def include_dirs(self):
        return [
            "{}/{}".format(
                self.ctx.include_dir,
                d.format(arch=self))
            for d in self.ctx.include_dirs]


    def get_env(self):
        include_dirs = [
            "-I{}/{}".format(
                self.ctx.include_dir,
                d.format(arch=self))
            for d in self.ctx.include_dirs]

        env = {}
        # AND: Have to find out what CC, AR and LD should be
        # env["CC"] = sh.xcrun("-find", "-sdk", self.sdk, "clang").strip()
        # env["AR"] = sh.xcrun("-find", "-sdk", self.sdk, "ar").strip()
        # env["LD"] = sh.xcrun("-find", "-sdk", self.sdk, "ld").strip()

        # AND: Added flags manually, removed $OFLAG
        # env["OTHER_CFLAGS"] = " ".join(
        #     include_dirs)

        # env["OTHER_LDFLAGS"] = " ".join([
        #     "-L{}/{}".format(self.ctx.dist_dir, "lib"),
        # ])

        env["CFLAGS"] = " ".join([
            "-DANDROID", "-mandroid", "-fomit-frame-pointer",
            "--sysroot", self.ctx.ndk_platform])
                              
        env["CXXFLAGS"] = env["CFLAGS"]
        
        env["LDFLAGS"] = " ".join(['-lm'])

        py_platform = sys.platform
        if py_platform in ['linux2', 'linux3']:
            py_platform = 'linux'

        if self.ctx.ndk_ver == 'r5b':
            toolchain_prefix = 'arm-eabi'
            toolchain_version = '4.4.0'
        elif self.ctx.ndk_ver[:2] == 'r7':
            toolchain_prefix = 'arm-linux-androideabi'
            toolchain_version = '4.4.3'
        elif self.ctx.ndk_ver[:2] == 'r9':
            toolchain_prefix = 'arm-linux-androideabi'
            toolchain_version = '4.9'
        else:
            print('Error: NDK not supported by these tools?')
            exit(1)

        env['TOOLCHAIN_PREFIX'] = toolchain_prefix
        env['TOOLCHAIN_VERSION'] = toolchain_version

        env['PATH'] = ('{ndk_dir}/toolchains/{toolchain_prefix}-{toolchain_version}/'
                       'prebuilt/{py_platform}-x86/bin/:{ndk_dir}/toolchains/'
                       '{toolchain_prefix}-{toolchain_version}/prebuilt/'
                       '{py_platform}-x86_64/bin/:{ndk_dir}:{sdk_dir}/'
                       'tools:{path}').format(
                           sdk_dir=self.ctx.sdk_dir, ndk_dir=self.ctx.ndk_dir,
                           toolchain_prefix=toolchain_prefix,
                           toolchain_version=toolchain_version,
                           py_platform=py_platform, path=environ.get('PATH'))

        cc = find_executable('{toolchain_prefix}-gcc'.format(
            toolchain_prefix=toolchain_prefix), path=env['PATH'])
        if cc is None:
            print('Couldn\'t find executable for CC. Exiting.')
            exit(1)

        env['CC'] = '{toolchain_prefix}-gcc {cflags}'.format(
            toolchain_prefix=toolchain_prefix,
            cflags=env['CFLAGS'])
        env['CXX'] = '{toolchain_prefix}-g++ {cxxflags}'.format(
            toolchain_prefix=toolchain_prefix,
            cxxflags=env['CXXFLAGS'])

        # AND: Not sure if these are still important
        env['AR'] = '{}-ar'.format(toolchain_prefix)
        env['RANLIB'] = '{}-ranlib'.format(toolchain_prefix)
        env['LD'] = '{}-ld'.format(toolchain_prefix)
        env['STRIP'] = '{}-strip --strip-unneeded'.format(toolchain_prefix)
        env['MAKE'] = 'make -j5'
        env['READELF'] = '{}-readelf'.format(toolchain_prefix)

        hostpython_recipe = Recipe.get_recipe('hostpython2', self.ctx)
        
        # AND: This hardcodes python version 2.7, needs fixing
        # AND: This also hardcodes armeabi, which isn't even correct, don't forget to fix!
        env['BUILDLIB_PATH'] = join(hostpython_recipe.get_build_dir('armeabi'),
                                    'build', 'lib.linux-{}-2.7'.format(uname()[-1]))


        # AND: This stuff is set elsewhere in distribute.sh. Does that matter?
        env['ARCH'] = self.arch
        env['LIBLINK_PATH'] = join(self.ctx.build_dir, 'other_builds', 'objects')
        ensure_dir(env['LIBLINK_PATH'])  # AND: This should be elsewhere
        env['LIBLINK'] = join(self.ctx.bootstrap.build_dir, 'tools', 'liblink')
        env['BIGLINK'] = join(self.ctx.bootstrap.build_dir, 'tools', 'biglink')

        return env


class ArchAndroid(Arch):
    arch = "armeabi"

# class ArchSimulator(Arch):
#     sdk = "iphonesimulator"
#     arch = "i386"
#     triple = "i386-apple-darwin11"
#     version_min = "-miphoneos-version-min=6.0.0"
#     sysroot = sh.xcrun("--sdk", "iphonesimulator", "--show-sdk-path").strip()


# class Arch64Simulator(Arch):
#     sdk = "iphonesimulator"
#     arch = "x86_64"
#     triple = "x86_64-apple-darwin13"
#     version_min = "-miphoneos-version-min=7.0"
#     sysroot = sh.xcrun("--sdk", "iphonesimulator", "--show-sdk-path").strip()


# class ArchIOS(Arch):
#     sdk = "iphoneos"
#     arch = "armv7"
#     triple = "arm-apple-darwin11"
#     version_min = "-miphoneos-version-min=6.0.0"
#     sysroot = sh.xcrun("--sdk", "iphoneos", "--show-sdk-path").strip()


# class Arch64IOS(Arch):
#     sdk = "iphoneos"
#     arch = "arm64"
#     triple = "aarch64-apple-darwin13"
#     version_min = "-miphoneos-version-min=7.0"
#     sysroot = sh.xcrun("--sdk", "iphoneos", "--show-sdk-path").strip()
    

class Graph(object):
    # Taken from python-for-android/depsort
    def __init__(self):
        # `graph`: dict that maps each package to a set of its dependencies.
        self.graph = {}

    def add(self, dependent, dependency):
        """Add a dependency relationship to the graph"""
        self.graph.setdefault(dependent, set())
        self.graph.setdefault(dependency, set())
        if dependent != dependency:
            self.graph[dependent].add(dependency)

    def add_optional(self, dependent, dependency):
        """Add an optional (ordering only) dependency relationship to the graph

        Only call this after all mandatory requirements are added
        """
        if dependent in self.graph and dependency in self.graph:
            self.add(dependent, dependency)

    def find_order(self):
        """Do a topological sort on a dependency graph

        :Parameters:
            :Returns:
                iterator, sorted items form first to last
        """
        graph = dict((k, set(v)) for k, v in self.graph.items())
        while graph:
            # Find all items without a parent
            leftmost = [l for l, s in graph.items() if not s]
            if not leftmost:
                raise ValueError('Dependency cycle detected! %s' % graph)
            # If there is more than one, sort them for predictable order
            leftmost.sort()
            for result in leftmost:
                # Yield and remove them from the graph
                yield result
                graph.pop(result)
                for bset in graph.values():
                    bset.discard(result)


class Context(object):
    env = environ.copy()
    root_dir = None  # the filepath of toolchain.py
    storage_dir = None  # the root dir where builds and dists will be stored
    build_dir = None  # in which bootstraps are copied for building and recipes are built
    dist_dir = None  # the Android project folder where everything ends up
    libs_dir = None
    javaclass_dir = None
    ccache = None  # whether to use ccache
    cython = None  # the cython interpreter name

    sdk_dir = None  # the directory of the android sdk
    ndk_dir = None  # the directory of the android ndk
    ndk_platform = None  # the ndk platform directory
    ndk_ver = None  # the ndk version, defaults to r9
    android_api = None  # the android api target, defaults to 14
    
    dist_name = None
    bootstrap = None 
    bootstrap_build_dir = None

    @property
    def packages_path(self):
        '''Where packages are downloaded before being unpacked'''
        return join(self.root_dir, '.packages')

    def setup_dirs(self):
        '''Calculates all the storage and build dirs, and makes sure
        the directories exist where necessary.'''
        self.root_dir = realpath(dirname(__file__))

        # AND: TODO: Allow the user to set the build_dir
        # self.storage_dir = user_data_dir('python-for-android')
        self.storage_dir = self.root_dir
        self.build_dir = join(self.storage_dir, 'build')
        self.libs_dir = join(self.build_dir, 'libs')
        self.dist_dir = join(self.storage_dir, 'dists')
        self.javaclass_dir = join(self.build_dir, 'java')

        ensure_dir(self.storage_dir)
        ensure_dir(self.build_dir)
        ensure_dir(self.libs_dir)
        ensure_dir(self.dist_dir)
        ensure_dir(self.javaclass_dir)

    def __init__(self):
        super(Context, self).__init__()
        self.include_dirs = []

        ok = True

        # AND: We should check for ndk-build and ant?
        self.android_api = environ.get('ANDROIDAPI', 14)
        self.ndk_ver = environ.get('ANDROIDNDKVER', 'r9')
        self.sdk_dir = environ.get('ANDROIDSDK', None)
        if self.sdk_dir is None:
            ok = False
        self.ndk_dir = environ.get('ANDROIDNDK', None)
        if self.ndk_dir is None:
            ok = False
        else:
            self.ndk_platform = join(
                self.ndk_dir,
                'platforms',
                'android-{}'.format(self.android_api),
                'arch-arm')
        if not exists(self.ndk_platform):
            print('ndk_platform doesn\'t exist')
            ok = False
                

        # AND: How to check that the sdk is available?

        # root of the toolchain
        self.setup_dirs()

        # AND: Currently only the Android architecture is supported
        self.archs = (
            ArchAndroid(self),
            )
        
        # path to some tools
        self.ccache = sh.which("ccache")
        if not self.ccache:
            print("ccache is missing, the build will not be optimized in the future.")
        for cython_fn in ("cython2", "cython-2.7", "cython"):
            cython = sh.which(cython_fn)
            if cython:
                self.cython = cython
                break
        if not self.cython:
            ok = False
            print("Missing requirement: cython is not installed")

        # AND: Are these necessary? Where to check for and and ndk-build?
        # check the basic tools
        for tool in ("pkg-config", "autoconf", "automake", "libtool",
                     "tar", "bzip2", "unzip", "make", "gcc", "g++"):
            if not sh.which(tool):
                print("Missing requirement: {} is not installed".format(
                    tool))

        if not ok:
            sys.exit(1)

        ensure_dir(join(self.build_dir, 'bootstrap_builds'))
        ensure_dir(join(self.build_dir, 'other_builds'))  # where everything else is built

        # # remove the most obvious flags that can break the compilation
        self.env.pop("LDFLAGS", None)
        self.env.pop("ARCHFLAGS", None)
        self.env.pop("CFLAGS", None)

        # set the state
        self.state = JsonStore(join(self.dist_dir, "state.db"))

    def prepare_bootstrap(self, bs):
        bs.ctx = self
        self.bootstrap = bs
        self.bootstrap.prepare_build_dir()
        self.bootstrap_build_dir = self.bootstrap.build_dir

    def prepare_dist(self, name):
        self.dist_name = name
        self.bootstrap.prepare_dist_dir(self.dist_name)



class Bootstrap(object):
    '''An Android project template, containing recipe stuff for
    compilation and templated fields for APK info.
    '''
    bootstrap_template_dir = ''
    jni_subdir = '/jni'
    ctx = None

    build_dir = None
    dist_dir = None
    dist_name = None

    recipe_depends = []
    

    # supported_recipes = [] # only necessary if we don't implement
    # jni dir copying

    # Other things a Bootstrap might need to track (maybe separately):
    # ndk_main.c
    # whitelist.txt
    # blacklist.txt
    #  


    @property
    def jni_dir(self):
        return self.bootstrap_template_dir + self.jni_subdir

    def prepare_build_dir(self):
        '''Ensure that a build dir exists for the recipe. This same single
        dir will be used for building all different archs.'''
        self.build_dir = join(self.ctx.build_dir, 'bootstrap_builds',
                              self.bootstrap_template_dir)
        shprint(sh.cp, '-r',
                join(self.ctx.root_dir,
                     'bootstrap_templates',
                     self.bootstrap_template_dir),
                self.build_dir)

    def prepare_dist_dir(self, name):
        self.dist_dir = join(self.ctx.dist_dir, name + '_' +
                             self.bootstrap_template_dir)
        # shprint(sh.cp, '-r',
        #         join(self.ctx.root_dir,
        #              'bootstrap_templates',
        #              self.bootstrap_template_dir),
        #         self.dist_dir)
        ensure_dir(self.dist_dir)

    def run_distribute(self):
        print('Default bootstrap being used doesn\'t know how to distribute...failing.')
        exit(1)


class PygameBootstrap(Bootstrap):
    bootstrap_template_dir = 'pygame'

    recipe_depends = ['hostpython2', 'python2', 'pyjnius', 'sdl', 'pygame',
                      'android', 'kivy']
    
    def run_distribute(self):
        info_main('# Creating Android project from build and {} bootstrap'.format(
            self.bootstrap_template_dir))

        src_path = join(self.ctx.root_dir, 'bootstrap_templates',
                        self.bootstrap_template_dir)
        
        with current_directory(self.dist_dir):

            info('Creating initial layout')
            for dirname in ('assets', 'bin', 'private', 'res', 'templates'):
                if not exists(dirname):
                    shprint(sh.mkdir, dirname)

            info('Copying default files')
            shprint(sh.cp, '-a', join(src_path, 'default.properties'), '.')
            shprint(sh.cp, '-a', join(src_path, 'local.properties'), '.')
            shprint(sh.cp, '-a', join(src_path, 'build.py'), '.')
            shprint(sh.cp, '-a', join(src_path, 'buildlib'), '.')
            shprint(sh.cp, '-a', join(src_path, 'src'), '.')
            shprint(sh.cp, '-a', join(src_path, 'templates'), '.')
            shprint(sh.cp, '-a', join(src_path, 'res'), '.')
            shprint(sh.cp, '-a', join(src_path, 'blacklist.txt'), '.')
            shprint(sh.cp, '-a', join(src_path, 'whitelist.txt'), '.')
            
            info('Copying python distribution')
            hostpython = sh.Command(self.ctx.hostpython)
            # AND: This *doesn't* need to be in arm env?
            shprint(hostpython, '-OO', '-m', 'compileall', join(self.ctx.build_dir, 'python-install'))
            if not exists('python-install'):
                shprint(sh.cp, '-a', join(self.ctx.build_dir, 'python-install'), '.')

            info('Copying libs')
            # AND: Hardcoding armeabi - naughty!
            shprint(sh.mkdir, '-p', join('libs', 'armeabi'))
            for lib in glob.glob(join(self.ctx.libs_dir, '*')):
                shprint(sh.cp, '-a', lib, join('libs', 'armeabi'))

            info('Copying java files')
            for filename in glob.glob(join(self.ctx.build_dir, 'java', '*')):
                shprint(sh.cp, '-a', filename, 'src')

            info('Filling private directory')
            if not exists(join('private', 'lib')):
                shprint(sh.cp, '-a', join('python-install', 'lib'), 'private')
            shprint(sh.mkdir, '-p', join('private', 'include', 'python2.7'))
            
            # AND: Copylibs stuff should go here
            shprint(sh.mv, join('libs', 'armeabi', 'libpymodules.so'), 'private/')
            shprint(sh.cp, join('python-install', 'include' , 'python2.7', 'pyconfig.h'), join('private', 'include', 'python2.7/'))

            info('Removing some unwanted files')
            shprint(sh.rm, '-f', join('private', 'lib', 'libpython2.7.so'))
            shprint(sh.rm, '-rf', join('private', 'lib', 'pkgconfig'))

            with current_directory(join(self.dist_dir, 'private', 'lib', 'python2.7')):
                # shprint(sh.xargs, 'rm', sh.grep('-E', '*\.(py|pyx|so\.o|so\.a|so\.libs)$', sh.find('.')))
                removes = []
                for dirname, something, filens in walk('.'):
                    for filename in filens:
                        for suffix in ('py', 'pyc', 'so.o', 'so.a', 'so.libs'):
                            if filename.endswith(suffix):
                                removes.append(filename)
                shprint(sh.rm, '-f', *removes)

                info('Deleting some other stuff not used on android')
                # To quote the original distribute.sh, 'well...'
                shprint(sh.rm, '-rf', 'ctypes')
                shprint(sh.rm, '-rf', 'lib2to3')
                shprint(sh.rm, '-rf', 'idlelib')
                for filename in glob.glob('config/libpython*.a'):
                    shprint(sh.rm, '-f', filename)
                shprint(sh.rm, '-rf', 'config/python.o')
                shprint(sh.rm, '-rf', 'lib-dynload/_ctypes_test.so')
                shprint(sh.rm, '-rf', 'lib-dynload/_testcapi.so')


        info('Stripping libraries')
        env = ArchAndroid(self.ctx).get_env()
        strip = which('arm-linux-androideabi-strip', env['PATH'])
        if strip is None:
            print('Can\'t find strip in PATH...')
        strip = sh.Command(strip)
        filens = shprint(sh.find, join(self.dist_dir, 'private'), join(self.dist_dir, 'libs'),
                '-iname', '*.so', _env=env).stdout
        logger.info('Stripping libraries in private dir')
        for filen in filens.split('\n'):
            try:
                strip(filen, _env=env)
            except sh.ErrorReturnCode_1:
                logger.debug('Failed to strip ' + 'filen')

        

class Recipe(object):
    version = None
    url = None
    md5sum = None
    depends = []
    conflicts = []

    name = None  # name for the recipe dir

    archs = ['armeabi']  # will android use this?

    # library = None
    # libraries = []
    # include_dir = None
    # include_per_arch = False
    # frameworks = []
    # sources = []

    @property
    def versioned_url(self):
        if self.url is None:
            return None
        return self.url.format(version=self.version)

    # API available for recipes
    def download_file(self, url, filename, cwd=None):
        """
        Download an `url` to `outfn`
        """
        if not url:
            return
        def report_hook(index, blksize, size):
            if size <= 0:
                progression = '{0} bytes'.format(index * blksize)
            else:
                progression = '{0:.2f}%'.format(
                        index * blksize * 100. / float(size))
            stdout.write('- Download {}\r'.format(progression))
            stdout.flush()

        if cwd:
            filename = join(cwd, filename)
        if exists(filename):
            unlink(filename)

        info('Downloading {} from {}'.format(self.name, url))
        urlretrieve(url, filename, report_hook)
        return filename

    def extract_file(self, filename, cwd):
        """
        Extract the `filename` into the directory `cwd`.
        """
        if not filename:
            return
        print("Extract {} into {}".format(filename, cwd))
        if filename.endswith(".tgz") or filename.endswith(".tar.gz"):
            shprint(sh.tar, "-C", cwd, "-xvzf", filename)

        elif filename.endswith(".tbz2") or filename.endswith(".tar.bz2"):
            shprint(sh.tar, "-C", cwd, "-xvjf", filename)

        elif filename.endswith(".zip"):
            zf = zipfile.ZipFile(filename)
            zf.extractall(path=cwd)
            zf.close()

        else:
            print("Error: cannot extract, unreconized extension for {}".format(
                filename))
            raise Exception()

    # def get_archive_rootdir(self, filename):
    #     if filename.endswith(".tgz") or filename.endswith(".tar.gz") or \
    #         filename.endswith(".tbz2") or filename.endswith(".tar.bz2"):
    #         archive = tarfile.open(filename)
    #         root = archive.next().path.split("/")
    #         return root[0]
    #     elif filename.endswith(".zip"):
    #         with zipfile.ZipFile(filename) as zf:
    #             return dirname(zf.namelist()[0])
    #     else:
    #         print("Error: cannot detect root directory")
    #         print("Unrecognized extension for {}".format(filename))
    #         raise Exception()

    def apply_patch(self, filename):
        """
        Apply a patch from the current recipe directory into the current
        build directory.
        """
        info("Applying patch {}".format(filename))
        filename = join(self.recipe_dir, filename)
        # AND: get_build_dir shouldn't need to hardcode armeabi
        sh.patch("-t", "-d", self.get_build_dir('armeabi'), "-p1", "-i", filename)

    def copy_file(self, filename, dest):
        print("Copy {} to {}".format(filename, dest))
        filename = join(self.recipe_dir, filename)
        dest = join(self.build_dir, dest)
        shutil.copy(filename, dest)

    def append_file(self, filename, dest):
        print("Append {} to {}".format(filename, dest))
        filename = join(self.recipe_dir, filename)
        dest = join(self.build_dir, dest)
        with open(filename, "rb") as fd:
            data = fd.read()
        with open(dest, "ab") as fd:
            fd.write(data)

    # def has_marker(self, marker):
    #     """
    #     Return True if the current build directory has the marker set
    #     """
    #     return exists(join(self.build_dir, ".{}".format(marker)))

    # def set_marker(self, marker):
    #     """
    #     Set a marker info the current build directory
    #     """
    #     with open(join(self.build_dir, ".{}".format(marker)), "w") as fd:
    #         fd.write("ok")

    # def delete_marker(self, marker):
    #     """
    #     Delete a specific marker
    #     """
    #     try:
    #         unlink(join(self.build_dir, ".{}".format(marker)))
    #     except:
    #         pass


    @property
    def name(self):
        modname = self.__class__.__module__
        return modname.split(".", 1)[-1]

    # @property
    # def archive_fn(self):
    #     bfn = basename(self.url.format(version=self.version))
    #     fn = "{}/{}-{}".format(
    #         self.ctx.cache_dir,
    #         self.name, bfn)
    #     return fn

    # @property
    # def filtered_archs(self):
    #     result = []
    #     for arch in self.ctx.archs:
    #         if not self.archs or (arch.arch in self.archs):
    #             result.append(arch)
    #     return result

    # @property
    # def dist_libraries(self):
    #     libraries = []
    #     name = self.name
    #     if not name.startswith("lib"):
    #         name = "lib{}".format(name)
    #     if self.library:
    #         static_fn = join(self.ctx.dist_dir, "lib", "{}.a".format(name))
    #         libraries.append(static_fn)
    #     for library in self.libraries:
    #         static_fn = join(self.ctx.dist_dir, "lib", basename(library))
    #         libraries.append(static_fn)
    #     return libraries

    def get_build_container_dir(self, arch):
        '''Given the arch name, returns the directory where it will be built.'''
        return join(self.ctx.build_dir, 'other_builds', self.name, arch)

    def get_build_dir(self, arch):
        '''Given the arch name, returns the directory where the
        downloaded/copied package will be built.'''

        if self.url is not None:
            return join(self.get_build_container_dir(arch),
                        get_directory(self.versioned_url))
        return join(self.get_build_container_dir(arch), self.name)

    def get_recipe_dir(self):
        # AND: Redundant, an equivalent property is already set by get_recipe
        return join(self.ctx.root_dir, 'recipes', self.name)

    # Public Recipe API to be subclassed if needed

    # def init_with_ctx(self, ctx):
    #     self.ctx = ctx
    #     include_dir = None
    #     if self.include_dir:
    #         if self.include_per_arch:
    #             include_dir = join("{arch.arch}", self.name)
    #         else:
    #             include_dir = join("common", self.name)
    #     if include_dir:
    #         #print("Include dir added: {}".format(include_dir))
    #         self.ctx.include_dirs.append(include_dir)

    def ensure_build_container_dir(self):
        info_main('Preparing build dir for {}'.format(self.name))

        build_dir = self.get_build_container_dir('armeabi')
        ensure_dir(build_dir)
        
    def download_if_necessary(self):
        info_main('Downloading {}'.format(self.name))
        user_dir = environ.get('P4A_{}_DIR'.format(self.name.lower()))
        if user_dir is not None:
            info('P4A_{}_DIR is set, skipping download for {}'.format(
                self.name, self.name))
            return
        self.download()
        
    def download(self):
        if self.url is None:
            info('Skipping {} download as no URL is set'.format(self.name))
            return

        url = self.versioned_url

        shprint(sh.mkdir, '-p', join(self.ctx.packages_path, self.name))

        with current_directory(join(self.ctx.packages_path, self.name)):
            filename = shprint(sh.basename, url).stdout[:-1]

            do_download = True

            marker_filename = '.mark-{}'.format(filename)
            if exists(filename):
                if not exists(marker_filename):
                    shprint(sh.rm, filename)
                elif self.md5sum:
                    current_md5 = shprint(sh.md5sum, filename)
                    print('downloaded md5: {}'.format(current_md5))
                    print('expected md5: {}'.format(self.md5sum))
                    print('md5 not handled yet, exiting')
                    exit(1)
                else:
                    do_download = False
                    info('{} download already cached, skipping'.format(self.name))

            # Should check headers here!
            warning('Should check headers here! Skipping for now.')

            # If we got this far, we will download
            if do_download:
                print('Downloading {} from {}'.format(self.name, url))

                shprint(sh.rm, '-f', marker_filename)
                self.download_file(url, filename)
                shprint(sh.touch, marker_filename)

                if self.md5sum is not None:
                    print('downloaded md5: {}'.format(current_md5))
                    print('expected md5: {}'.format(self.md5sum))
                    print('md5 not handled yet, exiting')
                    exit(1)

    def unpack(self, arch):
        info_main('Unpacking {} for {}'.format(self.name, arch))

        build_dir = self.get_build_container_dir(arch)

        user_dir = environ.get('P4A_{}_DIR'.format(self.name.lower()))
        if user_dir is not None:
            info('P4A_{}_DIR exists, symlinking instead'.format(
                self.name.lower()))
            # AND: Currently there's something wrong if I use ln, fix this
            warning('Using git clone instead of symlink...fix this!')
            if exists(self.get_build_dir(arch)):
                return
            shprint(sh.rm, '-rf', build_dir)
            shprint(sh.mkdir, '-p', build_dir)
            shprint(sh.rmdir, build_dir)
            ensure_dir(build_dir)
            # shprint(sh.ln, '-s', user_dir, join(build_dir, get_directory(self.versioned_url)))
            shprint(sh.git, 'clone', user_dir, self.get_build_dir('armeabi'))
            return

        if self.url is None:
            info('Skipping {} unpack as no URL is set'.format(self.name))
            return

        filename = shprint(sh.basename, self.versioned_url).stdout[:-1]
        
        # AND: TODO: Use tito's better unpacking method
        with current_directory(build_dir):
            directory_name = get_directory(filename)

            if not exists(directory_name) or not isdir(directory_name):
                extraction_filename = join(self.ctx.packages_path, self.name, filename)
                if (extraction_filename.endswith('.tar.gz') or
                    extraction_filename.endswith('.tgz')):
                    sh.tar('xzf', extraction_filename)
                    root_directory = shprint(sh.tar, 'tzf', extraction_filename).stdout.split('\n')[0].strip('/')
                    if root_directory != directory_name:
                        shprint(sh.mv, root_directory, directory_name)
                elif (extraction_filename.endswith('.tar.bz2') or
                      extraction_filename.endswith('.tbz2')):
                    info('Extracting {} at {}'.format(extraction_filename, filename))
                    sh.tar('xjf', extraction_filename)
                    root_directory = sh.tar('tjf', extraction_filename).stdout.split('\n')[0].strip('/')
                    if root_directory != directory_name:
                        shprint(sh.mv, root_directory, directory_name)
                elif extraction_filename.endswith('.zip'):
                    sh.unzip(extraction_filename)
                    import zipfile
                    fileh = zipfile.ZipFile(extraction_filename, 'r')
                    root_directory = fileh.filelist[0].filename.strip('/')
                    if root_directory != directory_name:
                        shprint(sh.mv, root_directory, directory_name)
                    # root_directory = shprint(sh.unzip, '-l'
                    # if root_directory != directory_name:
                    #     print('root dir is', root_directory, 'but expected dir is',
                    #           extraction_filename, '?')
                    #     exit(1)
                    
                        
            else:
                info('{} is already unpacked, skipping'.format(self.name))
            

    def get_recipe_env(self, arch=None):
        """Return the env specialized for the recipe
        """
        if arch is None:
            arch = self.filtered_archs[0]
        return arch.get_env()

    # @property
    # def archive_root(self):
    #     key = "{}.archive_root".format(self.name)
    #     value = self.ctx.state.get(key)
    #     if not key:
    #         value = self.get_archive_rootdir(self.archive_fn)
    #         self.ctx.state[key] = value
    #     return value

    def execute(self):
        if self.custom_dir:
            self.ctx.state.remove_all(self.name)
        self.download()
        self.extract()
        self.build_all()

    # AND: Will need to change how this works
    @property
    def custom_dir(self):
        """Check if there is a variable name to specify a custom version /
        directory to use instead of the current url.
        """
        d = environ.get("P4A_{}_DIR".format(self.name.lower()))
        if not d:
            return
        if not exists(d):
            return
        return d

    # @cache_execution
    # def download(self):
    #     key = "{}.archive_root".format(self.name)
    #     if self.custom_dir:
    #         self.ctx.state[key] = basename(self.custom_dir)
    #     else:
    #         src_dir = join(self.recipe_dir, self.url)
    #         if exists(src_dir):
    #             self.ctx.state[key] = basename(src_dir)
    #             return
    #         fn = self.archive_fn
    #         if not exists(fn):
    #             self.download_file(self.url.format(version=self.version), fn)
    #         self.ctx.state[key] = self.get_archive_rootdir(self.archive_fn)

    # @cache_execution
    def extract(self):
        # recipe tmp directory
        for arch in self.filtered_archs:
            print("Extract {} for {}".format(self.name, arch.arch))
            self.extract_arch(arch.arch)

    # def extract_arch(self, arch):
    #     build_dir = join(self.ctx.build_dir, self.name, arch)
    #     dest_dir = join(build_dir, self.archive_root)
    #     if self.custom_dir:
    #         if exists(dest_dir):
    #             shutil.rmtree(dest_dir)
    #         shutil.copytree(self.custom_dir, dest_dir)
    #     else:
    #         if exists(dest_dir):
    #             return
    #         src_dir = join(self.recipe_dir, self.url)
    #         if exists(src_dir):
    #             shutil.copytree(src_dir, dest_dir)
    #             return
    #         ensure_dir(build_dir)
    #         self.extract_file(self.archive_fn, build_dir) 

    # @cache_execution
    # def build(self, arch):
    #     self.build_dir = self.get_build_dir(arch.arch)
    #     if self.has_marker("building"):
    #         print("Warning: {} build for {} has been incomplete".format(
    #             self.name, arch.arch))
    #         print("Warning: deleting the build and restarting.")
    #         shutil.rmtree(self.build_dir)
    #         self.extract_arch(arch.arch)

    #     if self.has_marker("build_done"):
    #         print("Build python for {} already done.".format(arch.arch))
    #         return

    #     self.set_marker("building")

    #     chdir(self.build_dir)
    #     print("Prebuild {} for {}".format(self.name, arch.arch))
    #     self.prebuild_arch(arch)
    #     print("Build {} for {}".format(self.name, arch.arch))
    #     self.build_arch(arch)
    #     print("Postbuild {} for {}".format(self.name, arch.arch))
    #     self.postbuild_arch(arch)
    #     self.delete_marker("building")
    #     self.set_marker("build_done")

    # @cache_execution
    def build_all(self):
        filtered_archs = self.filtered_archs
        print("Build {} for {} (filtered)".format(
            self.name,
            ", ".join([x.arch for x in filtered_archs])))
        for arch in self.filtered_archs:
            self.build(arch)

        name = self.name
        if self.library:
            print("Create lipo library for {}".format(name))
            if not name.startswith("lib"):
                name = "lib{}".format(name)
            static_fn = join(self.ctx.dist_dir, "lib", "{}.a".format(name))
            ensure_dir(dirname(static_fn))
            print("Lipo {} to {}".format(self.name, static_fn))
            self.make_lipo(static_fn)
        if self.libraries:
            print("Create multiple lipo for {}".format(name))
            for library in self.libraries:
                static_fn = join(self.ctx.dist_dir, "lib", basename(library))
                ensure_dir(dirname(static_fn))
                print("  - Lipo-ize {}".format(library))
                self.make_lipo(static_fn, library)
        print("Install include files for {}".format(self.name))
        self.install_include()
        print("Install frameworks for {}".format(self.name))
        self.install_frameworks()
        print("Install sources for {}".format(self.name))
        self.install_sources()
        print("Install {}".format(self.name))
        self.install()

    def prebuild(self):
        self.prebuild_arch(self.ctx.archs[0])  # AND: Need to change
                                               # this to support
                                               # multiple archs

    def build(self):
        self.build_arch(self.ctx.archs[0])  # Same here!

    def postbuild(self):
        self.postbuild_arch(self.ctx.archs[0])

    def prebuild_arch(self, arch):
        info_main('Prebuilding {} for {}'.format(self.name, arch.arch))
        prebuild = "prebuild_{}".format(arch.arch)
        if hasattr(self, prebuild):
            getattr(self, prebuild)()
        else:
            print('{} has no {}, skipping'.format(self.name, prebuild))

    def build_arch(self, arch):
        info_main('Building {} for {}'.format(self.name, arch.arch))
        build = "build_{}".format(arch.arch)
        if hasattr(self, build):
            getattr(self, build)()

    def postbuild_arch(self, arch):
        info_main('Postbuilding {} for {}'.format(self.name, arch.arch))
        postbuild = "postbuild_{}".format(arch.arch)
        if hasattr(self, postbuild):
            getattr(self, postbuild)()

    # @cache_execution
    def make_lipo(self, filename, library=None):
        if library is None:
            library = self.library
        if not library:
            return
        args = []
        for arch in self.filtered_archs:
            library_fn = library.format(arch=arch)
            args += [
                "-arch", arch.arch,
                join(self.get_build_dir(arch.arch), library_fn)]
        shprint(sh.lipo, "-create", "-output", filename, *args)

    # @cache_execution
    def install_frameworks(self):
        if not self.frameworks:
            return
        arch = self.filtered_archs[0]
        build_dir = self.get_build_dir(arch.arch)
        for framework in self.frameworks:
            print(" - Install {}".format(framework))
            src = join(build_dir, framework)
            dest = join(self.ctx.dist_dir, "frameworks", framework)
            ensure_dir(dirname(dest))
            if exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(src, dest)

    # @cache_execution
    def install_sources(self):
        if not self.sources:
            return
        arch = self.filtered_archs[0]
        build_dir = self.get_build_dir(arch.arch)
        for source in self.sources:
            print(" - Install {}".format(source))
            src = join(build_dir, source)
            dest = join(self.ctx.dist_dir, "sources", self.name)
            ensure_dir(dirname(dest))
            if exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(src, dest)

    # @cache_execution
    def install_include(self):
        if not self.include_dir:
            return
        if self.include_per_arch:
            archs = self.ctx.archs
        else:
            archs = self.filtered_archs[:1]

        include_dirs = self.include_dir
        if not isinstance(include_dirs, (list, tuple)):
            include_dirs = list([include_dirs])

        for arch in archs:
            arch_dir = "common"
            if self.include_per_arch:
                arch_dir = arch.arch
            dest_dir = join(self.ctx.include_dir, arch_dir, self.name)
            if exists(dest_dir):
                shutil.rmtree(dest_dir)
            build_dir = self.get_build_dir(arch.arch)

            for include_dir in include_dirs:
                dest_name = None
                if isinstance(include_dir, (list, tuple)):
                    include_dir, dest_name = include_dir
                include_dir = include_dir.format(arch=arch, ctx=self.ctx)
                src_dir = join(build_dir, include_dir)
                if dest_name is None:
                    dest_name = basename(src_dir)
                if isdir(src_dir):
                    shutil.copytree(src_dir, dest_dir)
                else:
                    dest = join(dest_dir, dest_name)
                    print("Copy {} to {}".format(src_dir, dest))
                    ensure_dir(dirname(dest))
                    shutil.copy(src_dir, dest)

    # @cache_execution
    def install(self):
        pass

    @classmethod
    def list_recipes(cls):
        recipes_dir = join(dirname(__file__), "recipes")
        for name in listdir(recipes_dir):
            fn = join(recipes_dir, name)
            if isdir(fn):
                yield name

    @classmethod
    def get_recipe(cls, name, ctx):
        if not hasattr(cls, "recipes"):
           cls.recipes = {}
        if name in cls.recipes:
            return cls.recipes[name]
        mod = importlib.import_module("recipes.{}".format(name))
        if len(logger.handlers) > 1:
            logger.removeHandler(logger.handlers[1])
        recipe = mod.recipe
        recipe.recipe_dir = join(ctx.root_dir, "recipes", name)
        recipe.ctx = ctx
        return recipe


class NDKRecipe(Recipe):
    '''A recipe class for recipes built in an Android project jni dir with
    an Android.mk. These are not cached separatly, but built in the
    bootstrap's own building directory.

    In the future they should probably also copy their contents from a
    standalone set of ndk recipes, but for now the bootstraps include
    all their recipe code.

    '''
    
    def get_build_dir(self):
        return join(self.ctx.bootstrap.build_dir, 'jni', self.name)

    def get_jni_dir(self):
        return join(self.ctx.bootstrap.build_dir, 'jni')

    def download_if_necessary(self):
        info_main('Downloading {}'.format(self.name))
        info('{} is an NDK recipe, it is alread included in the '
              'bootstrap (for now), so skipping'.format(self.name))
        # Do nothing; in the future an NDKRecipe can copy its
        # contents to the bootstrap build dir, but for now each
        # bootstrap already includes available recipes (as was
        # already the case in p4a)

    def unpack(self, arch):
        info_main('Unpacking {} for {}'.format(self.name, arch))
        info('{} is included in the bootstrap, unpacking currently '
             'unnecessary, so skipping'.format(self.name))
        

class PythonRecipe(Recipe):
    pass
    # @cache_execution
    # def install(self):
    #     self.install_python_package()
    #     self.reduce_python_package()

    # def install_python_package(self, name=None, env=None, is_dir=True):
    #     """Automate the installation of a Python package into the target
    #     site-packages.

    #     It will works with the first filtered_archs, and the name of the recipe.
    #     """
    #     arch = self.filtered_archs[0]
    #     if name is None:
    #         name = self.name
    #     if env is None:
    #         env = self.get_recipe_env(arch)

    #     print("Install {} into the site-packages".format(name))
    #     build_dir = self.get_build_dir(arch.arch)
    #     chdir(build_dir)
    #     hostpython = sh.Command(self.ctx.hostpython)
    #     iosbuild = join(build_dir, "iosbuild")
    #     shprint(hostpython, "setup.py", "install", "-O2",
    #             "--prefix", iosbuild,
    #             _env=env)
    #     dest_dir = join(self.ctx.site_packages_dir, name)
    #     if is_dir:
    #         if exists(dest_dir):
    #             shutil.rmtree(dest_dir)
    #         func = shutil.copytree
    #     else:
    #         func = shutil.copy
    #     func(
    #         join(iosbuild, "lib",
    #              self.ctx.python_ver_dir, "site-packages", name),
    #         dest_dir)

    # def reduce_python_package(self):
    #     """Feel free to remove things you don't want in the final
    #     site-packages.
    #     """
    #     pass


class CythonRecipe(PythonRecipe):
    pre_build_ext = False
    cythonize = True

    # def cythonize_file(self, filename):
    #     if filename.startswith(self.build_dir):
    #         filename = filename[len(self.build_dir) + 1:]
    #     print("Cythonize {}".format(filename))
    #     cmd = sh.Command(join(self.ctx.root_dir, "tools", "cythonize.py"))
    #     shprint(cmd, filename)

    # def cythonize_build(self):
    #     if not self.cythonize:
    #         return
    #     root_dir = self.build_dir
    #     for root, dirnames, filenames in walk(root_dir):
    #         for filename in fnmatch.filter(filenames, "*.pyx"):
    #             self.cythonize_file(join(root, filename))

    def biglink(self):
        dirs = []
        for root, dirnames, filenames in walk(self.build_dir):
            if fnmatch.filter(filenames, "*.so.libs"):
                dirs.append(root)
        cmd = sh.Command(join(self.ctx.root_dir, "tools", "biglink"))
        shprint(cmd, join(self.build_dir, "lib{}.a".format(self.name)), *dirs)

    # def get_recipe_env(self, arch):
    #     env = super(CythonRecipe, self).get_recipe_env(arch)
    #     env["KIVYIOSROOT"] = self.ctx.root_dir
    #     env["IOSSDKROOT"] = arch.sysroot
    #     env["LDSHARED"] = join(self.ctx.root_dir, "tools", "liblink")
    #     env["ARM_LD"] = env["LD"]
    #     env["ARCH"] = arch.arch
    #     return env

    # def build_arch(self, arch):
    #     build_env = self.get_recipe_env(arch)
    #     hostpython = sh.Command(self.ctx.hostpython)
    #     if self.pre_build_ext:
    #         try:
    #             shprint(hostpython, "setup.py", "build_ext", "-g",
    #                     _env=build_env)
    #         except:
    #             pass
    #     self.cythonize_build()
    #     shprint(hostpython, "setup.py", "build_ext", "-g",
    #             _env=build_env)
    #     self.biglink()


def build_recipes(names, ctx):
    # Put recipes in correct build order
    graph = Graph()
    recipe_to_load = set(names)
    bs = ctx.bootstrap
    if bs.recipe_depends:
        info('Bootstrap requires recipes {}'.format(bs.recipe_depends))
        recipe_to_load = recipe_to_load.union(set(bs.recipe_depends))
    recipe_to_load = list(recipe_to_load)
    recipe_loaded = []
    while recipe_to_load:
        name = recipe_to_load.pop(0)
        if name in recipe_loaded:
            continue
        try:
            recipe = Recipe.get_recipe(name, ctx)
        except ImportError:
            print('Error: No recipe named {}'.format(name))
            sys.exit(1)
        graph.add(name, name)
        info('Loaded recipe {} (depends on {})'.format(name, recipe.depends))
        for depend in recipe.depends:
            graph.add(name, depend)
            recipe_to_load += recipe.depends
        recipe_loaded.append(name)
    build_order = list(graph.find_order())
    info("Recipe build order is {}".format(build_order))
    ctx.recipe_build_order = build_order

    recipes = [Recipe.get_recipe(name, ctx) for name in build_order]

    for recipe in recipes:
        recipe.download_if_necessary()

    for arch in ctx.archs:
        info_main('# Building all recipes for {}'.format(arch.arch))

        for recipe in recipes:
            ensure_dir(recipe.get_build_container_dir(arch.arch))
            recipe.unpack(arch.arch)

        # 2) prebuild packages
        for recipe in recipes:
            recipe.prebuild()

        # 3) build packages
        for recipe in recipes:
            recipe.build()

        # 4) biglink everything
        # AND: Should make this optional (could use 
        biglink(ctx)

        # 5) postbuild packages
        for recipe in recipes:
            recipe.postbuild()
    
    return

def run_pymodules_install(modules):
    warning('Pymodules can\'t currently be installed. Skipping.')
    if len(modules):
        print('Asked to build some python modules. Refusing!')
        exit(1)
        

def biglink(ctx):
    # AND: Shouldn't hardcode ArchAndroid! In reality need separate
    # build dirs for each arch
    env = ArchAndroid(ctx).get_env()

    print('Biglinking')
    bl = sh.Command(env['BIGLINK'])
    shprint(bl, join(ctx.libs_dir, 'libpymodules.so'),
            env['LIBLINK_PATH'], _env=env)



def ensure_dir(filename):
    if not exists(filename):
        makedirs(filename)

if __name__ == "__main__":
    import argparse
    
    class ToolchainCL(object):
        def __init__(self):
            parser = argparse.ArgumentParser(
                    description="Tool for managing the iOS / Python toolchain",
                    usage="""toolchain <command> [<args>]

Currently available commands:
    create_android_project    Build an android project with all recipes
                    
Available commands:
    build         Build a specific recipe
    clean         Clean the build
    distclean     Clean the build and the result
    recipes       List all the available recipes
    status        List all the recipes and their build status
""")
            parser.add_argument("command", help="Command to run")
            args = parser.parse_args(sys.argv[1:2])
            if not hasattr(self, args.command):
                print('Unrecognized command')
                parser.print_help()
                exit(1)
            getattr(self, args.command)()

        # def build(self):
        #     parser = argparse.ArgumentParser(
        #             description="Build the toolchain")
        #     parser.add_argument("recipe", nargs="+", help="Recipe to compile")
        #     parser.add_argument("--arch", help="Restrict compilation to this arch")
        #     args = parser.parse_args(sys.argv[2:])

        #     ctx = Context()
        #     # if args.arch:
        #     #     archs = args.arch.split()
        #     #     ctx.archs = [arch for arch in ctx.archs if arch.arch in archs]
        #     #     print("Architectures restricted to: {}".format(archs))
        #     build_recipes(args.recipe, ctx)

        def recipes(self):
            parser = argparse.ArgumentParser(
                    description="List all the available recipes")
            parser.add_argument(
                    "--compact", action="store_true",
                    help="Produce a compact list suitable for scripting")
            args = parser.parse_args(sys.argv[2:])

            if args.compact:
                print(" ".join(list(Recipe.list_recipes())))
            else:
                ctx = Context()
                for name in Recipe.list_recipes():
                    recipe = Recipe.get_recipe(name, ctx)
                    print("{recipe.name:<12} {recipe.version:<8}".format(
                          recipe=recipe))
                    print('    depends: {recipe.depends}'.format(recipe=recipe))
                    print('    conflicts: {recipe.conflicts}'.format(recipe=recipe))

        def clean_all(self):
            parser = argparse.ArgumentParser(
                    description="Clean the build cache, downloads and dists")
            args = parser.parse_args(sys.argv[2:])
            ctx = Context()
            if exists(ctx.build_dir):
                shutil.rmtree(ctx.build_dir)
            if exists(ctx.dist_dir):
                shutil.rmtree(ctx.dist_dir)
            if exists(ctx.packages_path):
                shutil.rmtree(ctx.packages_path)

        def clean_dists(self):
            parser = argparse.ArgumentParser(
                    description="Delete any distributions that have been built.")
            args = parser.parse_args(sys.argv[2:])
            ctx = Context()
            if exists(ctx.dist_dir):
                shutil.rmtree(ctx.dist_dir)

        def clean_builds(self):
            parser = argparse.ArgumentParser(
                    description="Delete all build and download caches")
            args = parser.parse_args(sys.argv[2:])
            ctx = Context()
            if exists(ctx.dist_dir):
                shutil.rmtree(ctx.dist_dir)
            if exists(ctx.packages_path):
                shutil.rmtree(ctx.packages_path)
            
        def status(self):
            parser = argparse.ArgumentParser(
                    description="Give a status of the build")
            args = parser.parse_args(sys.argv[2:])
            ctx = Context()
            # AND: TODO

            print('This isn\'t implemented yet, but should list all currently existing '
                  'distributions, the modules they include, and all the build caches.')
            exit(1)


        def create(self):
            '''Create a distribution directory if it doesn't already exist, run
            any recipes if necessary, and build the apk.
            '''
            parser = argparse.ArgumentParser(
                description='Create a newAndroid project')
            parser.add_argument('--name', help='The name of the project')
            parser.add_argument('--bootstrap', help=('The name of the bootstrap type, \'pygame\' '
                                                   'or \'sdl2\''))
            parser.add_argument('--python_dir', help='Directory of your python code')
            parser.add_argument('--recipes', help='Recipes to include',
                                default='kivy,')
            args = parser.parse_args(sys.argv[2:])

            if args.bootstrap == 'pygame':
                bs = PygameBootstrap()
            else:
                raise ValueError('Invalid bootstrap name: {}'.format(args.bootstrap))
            info_main('# Creating dist with with pygame bootstrap')

            ctx = Context()
            ctx.dist_name = args.name
            ctx.prepare_bootstrap(bs)
            ctx.prepare_dist(ctx.dist_name)

            recipes = re.split('[, ]*', args.recipes)
            info('Requested recipes are' + str(recipes))
            
            build_recipes(recipes, ctx)

            info_main('# Installing pure Python modules')
            run_pymodules_install([])

            ctx.bootstrap.run_distribute()

            print('Done building recipes, exiting for now.')
            return

        def print_context_info(self):
            ctx = Context()
            for attribute in ('root_dir', 'build_dir', 'dist_dir', 'libs_dir',
                              'ccache', 'cython', 'sdk_dir', 'ndk_dir', 'ndk_platform',
                              'ndk_ver', 'android_api'):
                print('{} is {}'.format(attribute, getattr(ctx, attribute)))
            

        # def create(self):
        #     parser = argparse.ArgumentParser(
        #             description="Create a new xcode project")
        #     parser.add_argument("name", help="Name of your project")
        #     parser.add_argument("directory", help="Directory where your project live")
        #     args = parser.parse_args(sys.argv[2:])
            
        #     from cookiecutter.main import cookiecutter
        #     ctx = Context()
        #     template_dir = join(curdir, "tools", "templates")
        #     context = {
        #         "title": args.name,
        #         "project_name": args.name.lower(),
        #         "domain_name": "org.kivy.{}".format(args.name.lower()),
        #         "project_dir": realpath(args.directory),
        #         "version": "1.0.0",
        #         "dist_dir": ctx.dist_dir,
        #     }
        #     cookiecutter(template_dir, no_input=True, extra_context=context)
        #     filename = join(
        #             getcwd(),
        #             "{}-ios".format(args.name.lower()),
        #             "{}.xcodeproj".format(args.name.lower()),
        #             "project.pbxproj")
        #     update_pbxproj(filename)
        #     print("--")
        #     print("Project directory : {}-ios".format(
        #         args.name.lower()))
        #     print("XCode project     : {0}-ios/{0}.xcodeproj".format(
        #         args.name.lower()))

         
        # def update(self):
        #     parser = argparse.ArgumentParser(
        #             description="Update an existing xcode project")
        #     parser.add_argument("filename", help="Path to your project or xcodeproj")
        #     args = parser.parse_args(sys.argv[2:])


        #     filename = args.filename
        #     if not filename.endswith(".xcodeproj"):
        #         # try to find the xcodeproj
        #         from glob import glob
        #         xcodeproj = glob(join(filename, "*.xcodeproj"))
        #         if not xcodeproj:
        #             print("ERROR: Unable to find a xcodeproj in {}".format(filename))
        #             sys.exit(1)
        #         filename = xcodeproj[0]

        #     filename = join(filename, "project.pbxproj")
        #     if not exists(filename):
        #         print("ERROR: {} not found".format(filename))
        #         sys.exit(1)

        #     update_pbxproj(filename)
        #     print("--")
        #     print("Project {} updated".format(filename))


    ToolchainCL()
