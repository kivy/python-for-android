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
import os
import zipfile
import tarfile
import importlib
import io
import json
import glob
import shutil
import fnmatch
import re
from functools import wraps
from datetime import datetime
from distutils.spawn import find_executable
try:
    from urllib.request import FancyURLopener
except ImportError:
    from urllib import FancyURLopener

import argparse

from appdirs import user_data_dir

curdir = dirname(__file__)
sys.path.insert(0, join(curdir, "tools", "external"))

import sh
import logging
import contextlib
import imp

from colorama import Style, Fore


logger = logging.getLogger('p4a')
# logger.setLevel(logging.DEBUG)
if not hasattr(logger, 'touched'):  # Necessary as importlib reloads
                                    # this, which would add a second
                                    # handler and reset the level
    logger.setLevel(logging.INFO)
    logger.touched = True
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

    # If logging is not in DEBUG mode, trim the command if necessary
    if logger.level > logging.DEBUG:
        short_string = string
        if len(string) > 100:
            short_string = string[:100] + '... (and {} more)'.format(len(string) - 100)
        logger.info(short_string + Style.RESET_ALL)
    else:
        logger.debug(string + Style.RESET_ALL)
        
    output = command(*args, **kwargs)
    need_closing_newline = False
    for line in output:
        if logger.level > logging.DEBUG:
            string = '\r' + 'working ... ' + line[:100].replace('\n', '').rstrip() + ' ...'
            if len(string) < 20:
                continue
            if len(string) < 120:
                string = string + ' '*(120 - len(string))
            sys.stdout.write(string)
            sys.stdout.flush()
            need_closing_newline = True
        else:
            logger.debug(''.join([Style.DIM, '\t', line.rstrip()]))
    if logger.level > logging.DEBUG and need_closing_newline:
        print()
    return output

# shprint(sh.ls, '-lah')
# exit(1)


def require_prebuilt_dist(func):
    @wraps(func)
    def wrapper_func(self, args):
        ctx = self.ctx
        dist = self.dist
        if dist.needs_build:
            info('No dist exists that meets your requirements, so one will '
                 'be built.')
            args = build_dist_from_args(ctx, dist, args)
        func(args)
    return wrapper_func


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
    info('Unknown file extension for {}'.format(filename))
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
        elif self.ctx.ndk_ver[:2] in ('r7', 'r8'):
            toolchain_prefix = 'arm-linux-androideabi'
            toolchain_version = '4.4.3'
        elif self.ctx.ndk_ver[:2] == 'r9':
            toolchain_prefix = 'arm-linux-androideabi'
            toolchain_version = '4.9'
        else:
            warning('Error: NDK not supported by these tools?')
            exit(1)

        env['TOOLCHAIN_PREFIX'] = toolchain_prefix
        env['TOOLCHAIN_VERSION'] = toolchain_version

        cc = find_executable('{toolchain_prefix}-gcc'.format(
            toolchain_prefix=toolchain_prefix), path=environ['PATH'])
        if cc is None:
            warning('Couldn\'t find executable for CC. Exiting.')
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

        env['PATH'] = environ['PATH']

        # AND: This stuff is set elsewhere in distribute.sh. Does that matter?
        env['ARCH'] = self.arch

        # env['LIBLINK_PATH'] = join(self.ctx.build_dir, 'other_builds', 'objects')
        # ensure_dir(env['LIBLINK_PATH'])  # AND: This should be elsewhere

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

    recipe_build_order = None  # Will hold the list of all built recipes

    @property
    def packages_path(self):
        '''Where packages are downloaded before being unpacked'''
        return join(self.storage_dir, 'packages')

    @property
    def templates_dir(self):
        return join(self.root_dir, 'templates')

    def setup_dirs(self):
        '''Calculates all the storage and build dirs, and makes sure
        the directories exist where necessary.'''
        self.root_dir = realpath(dirname(__file__))

        # AND: TODO: Allow the user to set the build_dir
        self.storage_dir = user_data_dir('python-for-android')
        # self.storage_dir = self.root_dir
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
        self.android_api = environ.get('ANDROIDAPI', '14')
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
            warning('ndk_platform doesn\'t exist')
            ok = False
                
        virtualenv = None
        if virtualenv is None:
            virtualenv = sh.which('virtualenv2')
        if virtualenv is None:
            virtualenv = sh.which('virtualenv-2.7')
        if virtualenv is None:
            virtualenv = sh.which('virtualenv7')
        if virtualenv is None:
            raise IOError('Couldn\'t find a virtualenv executable, '
                          'you must install this to use p4a.')
        self.virtualenv = virtualenv
        info('Found virtualenv at {}'.format(virtualenv))

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
            info("ccache is missing, the build will not be optimized in the future.")
        for cython_fn in ("cython2", "cython-2.7", "cython"):
            cython = sh.which(cython_fn)
            if cython:
                self.cython = cython
                break
        if not self.cython:
            ok = False
            warning("Missing requirement: cython is not installed")

        # Modify the path so that sh finds modules appropriately
        py_platform = sys.platform
        if py_platform in ['linux2', 'linux3']:
            py_platform = 'linux'
        if self.ndk_ver == 'r5b':
            toolchain_prefix = 'arm-eabi'
            toolchain_version = '4.4.0'
        elif self.ndk_ver[:2] in ('r7', 'r8'):
            toolchain_prefix = 'arm-linux-androideabi'
            toolchain_version = '4.4.3'
        elif self.ndk_ver[:2] == 'r9':
            toolchain_prefix = 'arm-linux-androideabi'
            toolchain_version = '4.9'
        else:
            warning('Error: NDK not supported by these tools?')
            exit(1)
        environ['PATH'] = ('{ndk_dir}/toolchains/{toolchain_prefix}-{toolchain_version}/'
                           'prebuilt/{py_platform}-x86/bin/:{ndk_dir}/toolchains/'
                           '{toolchain_prefix}-{toolchain_version}/prebuilt/'
                           '{py_platform}-x86_64/bin/:{ndk_dir}:{sdk_dir}/'
                           'tools:{path}').format(
                               sdk_dir=self.sdk_dir, ndk_dir=self.ndk_dir,
                               toolchain_prefix=toolchain_prefix,
                               toolchain_version=toolchain_version,
                               py_platform=py_platform, path=environ.get('PATH'))

        # AND: Are these necessary? Where to check for and and ndk-build?
        # check the basic tools
        for tool in ("pkg-config", "autoconf", "automake", "libtool",
                     "tar", "bzip2", "unzip", "make", "gcc", "g++"):
            if not sh.which(tool):
                warning("Missing requirement: {} is not installed".format(
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

    def get_site_packages_dir(self, arch=None):
        '''Returns the location of site-packages in the python-install build
        dir.
        '''

        # AND: This *must* be replaced with something more general in
        # order to support multiple python versions and/or multiple
        # archs.
        return join(self.build_dir, 'python-install', 'lib', 'python2.7',
                    'site-packages')

    def get_libs_dir(self, arch):
        '''The libs dir for a given arch.'''
        ensure_dir(join(self.libs_dir, arch))
        # AND: See warning:
        warning('Ensuring libs dir in get_libs_dir, should fix this '
                'to ensure elsewhere')
        return join(self.libs_dir, arch)


class Distribution(object):
    '''State container for information about a distribution (i.e. an
    Android project).

    This is separate from a Bootstrap because the Bootstrap is
    concerned with building and populating the dist directory, whereas
    the dist itself could also come from e.g. a binary download.
    '''
    ctx = None
    
    name = None  # A name identifying the dist. May not be None.
    needs_build = False  # Whether the dist needs compiling
    url = None
    dist_dir = None  # Where the dist dir ultimately is. Should not be None.

    recipes = []

    description = ''  # A long description

    def __init__(self, ctx):
        self.ctx = ctx

    def __str__(self):
        return '<Distribution: name {} with recipes ({})>'.format(
            # self.name, ', '.join([recipe.name for recipe in self.recipes]))
            self.name, ', '.join(self.recipes))

    def __repr__(self):
        return str(self)

    @classmethod
    def get_distribution(cls, ctx, name=None, recipes=[], allow_download=True,
                         force_build=False,
                         allow_build=True, extra_dist_dirs=[],
                         require_perfect_match=False):
        '''Takes information about the distribution, and decides what kind of
        distribution it will be.

        If parameters conflict (e.g. a dist with that name already
        exists, but doesn't have the right set of recipes),
        an error is thrown.

        Parameters
        ----------
        name : str
            The name of the distribution. If a dist with this name already '
            exists, it will be used.
        recipes : list
            The recipes that the distribution must contain.
        allow_download : bool
            Whether binary dists may be downloaded.
        allow_build : bool
            Whether the distribution may be built from scratch if necessary.
            This is always False on e.g. Windows.
        force_download: bool
            If True, only downloaded dists are considered.
        force_build : bool
            If True, the dist is forced to be built locally.
        extra_dist_dirs : list
            Any extra directories in which to search for dists.
        require_perfect_match : bool
            If True, will only match distributions with precisely the 
            correct set of recipes.
        '''

        # AND: This whole function is a bit hacky, it needs checking
        # properly to make sure it follows logically correct
        # possibilities

        existing_dists = Distribution.get_distributions(ctx)
    
        needs_build = True  # whether the dist needs building, will be returned

        possible_dists = existing_dists

        # 0) Check if a dist with that name already exists
        if name is not None and name:
            possible_dists = [d for d in possible_dists if d.name == name]

        # 1) Check if any existing dists meet the requirements
        _possible_dists = []
        for dist in possible_dists:
            for recipe in recipes:
                if recipe not in dist.recipes:
                    break
            else:
                _possible_dists.append(dist)
        possible_dists = _possible_dists

        if possible_dists:
            info('Of the existing distributions, the following meet '
                 'the given requirements:')
            for dist in possible_dists:
                info('\tname {}: recipes ({})'.format(dist.name, ', '.join(dist.recipes)))
        else:
            info('No existsing dists meet the given requirements!')
                

        # If any dist has perfect recipes, return it
        for dist in possible_dists:
            if force_build:
                continue
            if (set(dist.recipes) == set(recipes) or
                (set(recipes).issubset(set(dist.recipes)) and not require_perfect_match)):
                info('{} has compatible recipes, using this one'.format(dist.name))
                return dist

        assert len(possible_dists) < 2

        if name is not None and possible_dists:
            info('Asked for dist with name {} with recipes ({}), but a dist '
                 'with this name already exists and has incompatible recipes '
                 '({})'.format(name, ', '.join(recipes), ', '.join(possible_dists[0].recipes)))
            info('No compatible dist found, so exiting.')
            exit(1)

        # # 2) Check if any downloadable dists meet the requirements

        # online_dists = [('testsdl2', ['hostpython2', 'sdl2_image',
        #                               'sdl2_mixer', 'sdl2_ttf',
        #                               'python2', 'sdl2',
        #                               'pyjniussdl2', 'kivysdl2'],
        #                  'https://github.com/inclement/sdl2-example-dist/archive/master.zip'), 
        #                  ]
        # _possible_dists = []
        # for dist_name, dist_recipes, dist_url in online_dists:
        #     for recipe in recipes:
        #         if recipe not in dist_recipes:
        #             break
        #     else:
        #         dist = Distribution(ctx)
        #         dist.name = dist_name
        #         dist.url = dist_url
        #         _possible_dists.append(dist)
        # # if _possible_dists
           	

        # If we got this far, we need to build a new dist
        dist = Distribution(ctx)
        dist.needs_build = True

        if name is None:
            filen = 'unnamed_dist_{}'
            i = 1
            while exists(join(ctx.dist_dir, filen.format(i))):
                i += 1
            name = filen.format(i)

        dist.name = name
        dist.dist_dir = join(ctx.dist_dir, dist.name)
        dist.recipes = recipes

        return dist


    @classmethod
    def get_distributions(cls, ctx, extra_dist_dirs=[]):
        '''Returns all the distributions found locally.'''
        if extra_dist_dirs:
            warning('extra_dist_dirs argument to get_distributions is not yet implemented')
            exit(1)
        dist_dir = ctx.dist_dir
        folders = glob.glob(join(dist_dir, '*'))
        for dir in extra_dist_dirs:
            folders.extend(glob.glob(join(dir, '*')))

        dists = []
        for folder in folders:
            if exists(join(folder, 'dist_info.json')):
                with open(join(folder, 'dist_info.json')) as fileh:
                    dist_info = json.load(fileh)
                dist = cls(ctx)
                dist.name = folder.split('/')[-1]  # AND: also equal
                                                   # to
                                                   # dist_info['dist_name']...which
                                                   # one should we
                                                   # use?
                dist.dist_dir = folder
                dist.needs_build = False
                dist.recipes = dist_info['recipes']
                dists.append(dist)
        return dists


    def save_info(self):
        '''
        Save information about the distribution in its dist_dir.
        '''
        with current_directory(self.dist_dir):
            info('Saving distribution info')
            with open('dist_info.json', 'w') as fileh:
                json.dump({'dist_name': self.name,
                           'recipes': self.ctx.recipe_build_order},
                          fileh)

    def load_info(self):
        with current_directory(self.dist_dir):
            filen = 'dist_info.json'
            if not exists(filen):
                return None
            with open('dist_info.json', 'r') as fileh:
                dist_info = json.load(fileh)
        return dist_info
            



class Bootstrap(object):
    '''An Android project template, containing recipe stuff for
    compilation and templated fields for APK info.
    '''
    name = ''
    jni_subdir = '/jni'
    ctx = None

    build_dir = None
    dist_dir = None
    dist_name = None
    distribution = None

    recipe_depends = []
    
    # Other things a Bootstrap might need to track (maybe separately):
    # ndk_main.c
    # whitelist.txt
    # blacklist.txt

    @property
    def dist_dir(self):
        if self.distribution is None:
            warning('Tried to access {}.dist_dir, but {}.distribution '
                    'is None'.format(self, self))
            exit(1)
        return self.distribution.dist_dir
        

    @property
    def jni_dir(self):
        return self.name + self.jni_subdir

    def get_build_dir(self):
        return join(self.ctx.build_dir, 'bootstrap_builds', self.name)

    def get_dist_dir(self, name):
        return join(self.ctx.dist_dir, name)

    @property
    def name(self):
        modname = self.__class__.__module__
        return modname.split(".", 2)[-1]

    def prepare_build_dir(self):
        '''Ensure that a build dir exists for the recipe. This same single
        dir will be used for building all different archs.'''
        self.build_dir = self.get_build_dir()
        shprint(sh.cp, '-r',
                join(self.bootstrap_dir, 'build'),
                # join(self.ctx.root_dir,
                #      'bootstrap_templates',
                #      self.name),
                self.build_dir)

    def prepare_dist_dir(self, name):
        # self.dist_dir = self.get_dist_dir(name)
        ensure_dir(self.dist_dir)

    def run_distribute(self):
        # print('Default bootstrap being used doesn\'t know how to distribute...failing.')
        # exit(1)
        with current_directory(self.dist_dir):
            info('Saving distribution info')
            with open('dist_info.json', 'w') as fileh:
                json.dump({'dist_name': self.ctx.dist_name,
                           'bootstrap': self.ctx.bootstrap.name,
                           'recipes': self.ctx.recipe_build_order},
                          fileh)

    # AND: This method must be replaced by manual dir setting, in
    # order to allow for user dirs
    # def get_bootstrap_dir(self):
    #     return(dirname(__file__))

    @classmethod
    def list_bootstraps(cls):
        bootstraps_dir = join(dirname(__file__), 'bootstraps')
        for name in listdir(bootstraps_dir):
            filen = join(bootstraps_dir, name)
            if isdir(filen):
                yield name

    @classmethod
    def get_bootstrap(cls, name, ctx):
        '''Returns an instance of a bootstrap with the given name.

        This is the only way you should access a bootstrap class, as
        it sets the bootstrap directory correctly.
        '''
        # AND: This method will need to check user dirs, and access
        # bootstraps in a slightly different way
        if not hasattr(cls, 'bootstraps'):
            cls.bootstraps = {}
        if name in cls.bootstraps:
            return cls.bootstraps[name]
        mod = importlib.import_module('pythonforandroid.bootstraps.{}'.format(name))
        if len(logger.handlers) > 1:
            logger.removeHandler(logger.handlers[1])
        bootstrap = mod.bootstrap
        bootstrap.bootstrap_dir = join(ctx.root_dir, 'bootstraps', name)
        bootstrap.ctx = ctx
        return bootstrap


class Recipe(object):
    url = None
    '''The address from which the recipe may be downloaded. This is not
    essential, it may be omitted if the source is available some other
    way, such as via the :class:`IncludedFilesBehaviour` mixin.

    If the url includes the version, you may (and probably should)
    replace this with ``{version}``, which will automatically be
    replaced by the :attr:`version` string during download.

    .. note:: Methods marked (internal) are used internally and you
              probably don't need to call them, but they are available
              if you want.
    '''

    version = None
    '''A string giving the version of the software the recipe describes,
    e.g. ``2.0.3`` or ``master``.'''

    
    md5sum = None
    '''The md5sum of the source from the :attr:`url`. Non-essential, but
    you should try to include this, it is used to check that the download
    finished correctly.
    '''
    
    depends = []
    '''A list containing the names of any recipes that this recipe depends on.
    '''
    
    conflicts = []
    # AND: Not currently used
    '''A list containing the names of any recipes that are known to be
    incompatible with this one.'''

    # patches = []
    # '''Filepaths (relative to the recipe script) for any pathches that are
    # to be applied. By default, these are applied in prebuild_arch, so
    # if you override this but want to use patches then don't forget to
    # call super().
    
    # name = None  # name for the recipe dir

    archs = ['armeabi']  # will android use this?


    @property
    def versioned_url(self):
        '''A property returning the url of the recipe with ``{version}``
        replaced by the :attr:`url`. If accessing the url, you should use this
        property, *not* access the url directly.'''
        if self.url is None:
            return None
        return self.url.format(version=self.version)

    def download_file(self, url, filename, cwd=None):
        """
        (internal) Download an ``url`` to a ``filename``.
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
        (internal) Extract the `filename` into the directory `cwd`.
        """
        if not filename:
            return
        info("Extract {} into {}".format(filename, cwd))
        if filename.endswith(".tgz") or filename.endswith(".tar.gz"):
            shprint(sh.tar, "-C", cwd, "-xvzf", filename)

        elif filename.endswith(".tbz2") or filename.endswith(".tar.bz2"):
            shprint(sh.tar, "-C", cwd, "-xvjf", filename)

        elif filename.endswith(".zip"):
            zf = zipfile.ZipFile(filename)
            zf.extractall(path=cwd)
            zf.close()

        else:
            warning("Error: cannot extract, unrecognized extension for {}".format(
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
        info("Copy {} to {}".format(filename, dest))
        filename = join(self.recipe_dir, filename)
        dest = join(self.build_dir, dest)
        shutil.copy(filename, dest)

    def append_file(self, filename, dest):
        info("Append {} to {}".format(filename, dest))
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
        return modname.split(".", 2)[-1]

    # @property
    # def archive_fn(self):
    #     bfn = basename(self.url.format(version=self.version))
    #     fn = "{}/{}-{}".format(
    #         self.ctx.cache_dir,
    #         self.name, bfn)
    #     return fn

    @property
    def filtered_archs(self):
        '''Return archs of self.ctx that are valid build archs for the Recipe.'''
        result = []
        for arch in self.ctx.archs:
            if not self.archs or (arch.arch in self.archs):
                result.append(arch)
        return result

    def get_build_container_dir(self, arch):
        '''Given the arch name, returns the directory where it will be built.'''
        return join(self.ctx.build_dir, 'other_builds', self.name, arch)

    def get_build_dir(self, arch):
        '''Given the arch name, returns the directory where the
        downloaded/copied package will be built.'''

        # if self.url is not None:
        #     return join(self.get_build_container_dir(arch),
        #                 get_directory(self.versioned_url))
        return join(self.get_build_container_dir(arch), self.name)

    def get_recipe_dir(self):
        # AND: Redundant, an equivalent property is already set by get_recipe
        return join(self.ctx.root_dir, 'recipes', self.name)

    # Public Recipe API to be subclassed if needed

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
            directory_name = self.get_build_dir(arch)

            # AND: Could use tito's get_archive_rootdir here
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
                else:
                    raise Exception('Could not extract {} download, it must be .zip, '
                                    '.tar.gz or .tar.bz2')
                        
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

    # def execute(self):
    #     if self.custom_dir:
    #         self.ctx.state.remove_all(self.name)
    #     self.download()
    #     self.extract()
    #     self.build_all()

    # AND: Will need to change how this works
    # @property
    # def custom_dir(self):
    #     """Check if there is a variable name to specify a custom version /
    #     directory to use instead of the current url.
    #     """
    #     d = environ.get("P4A_{}_DIR".format(self.name.lower()))
    #     if not d:
    #         return
    #     if not exists(d):
    #         return
    #     return d

    # def prebuild(self):
    #     self.prebuild_arch(self.ctx.archs[0])  # AND: Need to change
    #                                            # this to support
    #                                            # multiple archs

    # def build(self):
    #     self.build_arch(self.ctx.archs[0])  # Same here!

    # def postbuild(self):
    #     self.postbuild_arch(self.ctx.archs[0])

    def prebuild_arch(self, arch):
        prebuild = "prebuild_{}".format(arch.arch)
        if hasattr(self, prebuild):
            getattr(self, prebuild)()
        else:
            print('{} has no {}, skipping'.format(self.name, prebuild))

    def should_build(self):
        '''Should perform any necessary test and return True only if it needs
        building again.

        '''
        return True

    def build_arch(self, arch):
        build = "build_{}".format(arch.arch)
        if hasattr(self, build):
            getattr(self, build)()

    def postbuild_arch(self, arch):
        postbuild = "postbuild_{}".format(arch.arch)
        if hasattr(self, postbuild):
            getattr(self, postbuild)()

    def prepare_build_dir(self, arch):
        '''Copies the recipe data into a build dir for the given arch. By
        default, this unpacks a downloaded recipe. You should override
        it (or use a Recipe subclass with different behaviour) if you
        want to do something else.
        '''
        self.unpack(arch)

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
        mod = importlib.import_module("pythonforandroid.recipes.{}".format(name))
        if len(logger.handlers) > 1:
            logger.removeHandler(logger.handlers[1])
        recipe = mod.recipe
        recipe.recipe_dir = join(ctx.root_dir, "recipes", name)
        recipe.ctx = ctx
        return recipe


class IncludedFilesBehaviour(object):
    '''Recipe mixin class that will automatically unpack files included in
    the recipe directory.'''
    src_filename = None
    def prepare_build_dir(self, arch):
        if self.src_filename is None:
            print('IncludedFilesBehaviour failed: no src_filename specified')
            exit(1)
        shprint(sh.cp, '-a', join(self.get_recipe_dir(), self.src_filename),
                self.get_build_dir(arch))

class NDKRecipe(Recipe):
    '''A recipe class for recipes built in an Android project jni dir with
    an Android.mk. These are not cached separatly, but built in the
    bootstrap's own building directory.

    In the future they should probably also copy their contents from a
    standalone set of ndk recipes, but for now the bootstraps include
    all their recipe code.

    '''

    dir_name = None  # The name of the recipe build folder in the jni dir

    def get_build_container_dir(self, arch):
        return self.get_jni_dir()

    def get_build_dir(self, arch):
        if self.dir_name is None:
            raise ValueError('{} recipe doesn\'t define a dir_name, but '
                             'this is necessary'.format(self.name))
        return join(self.get_build_container_dir(arch), self.dir_name)

    def get_jni_dir(self):
        return join(self.ctx.bootstrap.build_dir, 'jni')

    # def download_if_necessary(self):
    #     info_main('Downloading {}'.format(self.name))
    #     info('{} is an NDK recipe, it is alread included in the '
    #           'bootstrap (for now), so skipping'.format(self.name))
    #     # Do nothing; in the future an NDKRecipe can copy its
    #     # contents to the bootstrap build dir, but for now each
    #     # bootstrap already includes available recipes (as was
    #     # already the case in p4a)

    # def prepare_build_dir(self, arch):
    #     info_main('Unpacking {} for {}'.format(self.name, arch))
    #     info('{} is included in the bootstrap, unpacking currently '
    #          'unnecessary, so skipping'.format(self.name))
        

class PythonRecipe(Recipe):
    site_packages_name = None  # The name of the module in
                               # site_packages (i.e. as a python
                               # module)

    def should_build(self):
        # AND: This should be different for each arch and use some
        # kind of data store to know what has been built in a given
        # python env
        print('name is', self.site_packages_name, type(self))
        name = self.site_packages_name
        if name is None:
            name = self.name
        if exists(join(self.ctx.get_site_packages_dir(), name)):
            info('Python package already exists in site-packages')
            return False
        print('site packages', self.ctx.get_site_packages_dir())
        info('{} apparently isn\'t already in site-packages'.format(name))
        return True
                       

    
    def build_arch(self, arch):
        '''Install the Python module by calling setup.py install with
        the target Python dir.'''
        super(PythonRecipe, self).build_arch(arch)
        self.install_python_package()
    # @cache_execution
    # def install(self):
    #     self.install_python_package()
    #     self.reduce_python_package()

    def install_python_package(self, name=None, env=None, is_dir=True):
        '''Automate the installation of a Python package (or a cython
        package where the cython components are pre-built).'''
        arch = self.filtered_archs[0]
        if name is None:
            name = self.name
        if env is None:
            env = self.get_recipe_env(arch)

        info('Installing {} into site-packages'.format(self.name))

        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)

            shprint(hostpython, 'setup.py', 'install', '-O2', _env=env)

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

class CompiledComponentsPythonRecipe(PythonRecipe):
    pre_build_ext = False
    def build_arch(self, arch):
        '''Build any cython components, then install the Python module by
        calling setup.py install with the target Python dir.
        '''
        Recipe.build_arch(self, arch)  # AND: Having to directly call the
                                 # method like this is nasty...could
                                 # use tito's method of having an
                                 # install method that always runs
                                 # after everything else but isn't
                                 # used by a normal recipe.
        self.build_compiled_components(arch)
        self.install_python_package()

    def build_compiled_components(self, arch):
        info('Building compiled components in {}'.format(self.name))
        
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)
            shprint(hostpython, 'setup.py', 'build_ext', '-v')
            build_dir = glob.glob('build/lib.*')[0]
            shprint(sh.find, build_dir, '-name', '"*.o"', '-exec',
                    env['STRIP'], '{}', ';', _env=env)
            

class CythonRecipe(PythonRecipe):
    pre_build_ext = False
    cythonize = True

    def build_arch(self, arch):
        '''Build any cython components, then install the Python module by
        calling setup.py install with the target Python dir.
        '''
        Recipe.build_arch(self, arch)  # AND: Having to directly call the
                                 # method like this is nasty...could
                                 # use tito's method of having an
                                 # install method that always runs
                                 # after everything else but isn't
                                 # used by a normal recipe.
        self.build_cython_components(arch)
        self.install_python_package()

    def build_cython_components(self, arch):
        # AND: Should we use tito's cythonize methods? How do they work?
        info('Cythonizing anything necessary in {}'.format(self.name))
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)
            info('Trying first build of {} to get cython files: this is '
                 'expected to fail'.format(self.name))
            try:
                shprint(hostpython, 'setup.py', 'build_ext', _env=env)
            except sh.ErrorReturnCode_1:
                print()
                info('{} first build failed (as expected)'.format(self.name))

            info('Running cython where appropriate')
            shprint(sh.find, self.get_build_dir('armeabi'), '-iname', '*.pyx', '-exec',
                    self.ctx.cython, '{}', ';', _env=env)
            info('ran cython')

            shprint(hostpython, 'setup.py', 'build_ext', '-v', _env=env)

            print('stripping')
            build_lib = glob.glob('./build/lib*')
            shprint(sh.find, build_lib[0], '-name', '*.o', '-exec',
                    env['STRIP'], '{}', ';', _env=env)
            print('stripped!?')
            # exit(1)
        
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

    # def biglink(self):
    #     dirs = []
    #     for root, dirnames, filenames in walk(self.build_dir):
    #         if fnmatch.filter(filenames, "*.so.libs"):
    #             dirs.append(root)
    #     cmd = sh.Command(join(self.ctx.root_dir, "tools", "biglink"))
    #     shprint(cmd, join(self.build_dir, "lib{}.a".format(self.name)), *dirs)

    def get_recipe_env(self, arch):
        env = super(CythonRecipe, self).get_recipe_env(arch)
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch))
        env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')
        env['LIBLINK'] = 'NOTNONE'
        env['NDKPLATFORM'] = self.ctx.ndk_platform

        # Every recipe uses its own liblink path, object files are collected and biglinked later
        liblink_path = join(self.get_build_container_dir(arch.arch), 'objects_{}'.format(self.name))
        env['LIBLINK_PATH'] = liblink_path
        ensure_dir(liblink_path)
        return env


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
    python_modules = []
    while recipe_to_load:
        name = recipe_to_load.pop(0)
        if name in recipe_loaded:
            continue
        try:
            recipe = Recipe.get_recipe(name, ctx)
        except ImportError:
            info('No recipe named {}; will attempt to install with pip'.format(name))
            python_modules.append(name)
            continue
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

    # download is arch independent
    info_main('# Downloading recipes ')
    for recipe in recipes:
        recipe.download_if_necessary()

    for arch in ctx.archs:
        info_main('# Building all recipes for arch {}'.format(arch.arch))

        info_main('# Unpacking recipes')
        for recipe in recipes:
            ensure_dir(recipe.get_build_container_dir(arch.arch))
            recipe.prepare_build_dir(arch.arch)

        info_main('# Prebuilding recipes')
        # 2) prebuild packages
        for recipe in recipes:
            info_main('Prebuilding {} for {}'.format(recipe.name, arch.arch))
            recipe.prebuild_arch(arch)

        # 3) build packages
        info_main('# Building recipes')
        for recipe in recipes:
            info_main('Building {} for {}'.format(recipe.name, arch.arch))
            if recipe.should_build():
                recipe.build_arch(arch)
            else:
                info('{} said it is already built, skipping'.format(recipe.name))

        # 4) biglink everything
        # AND: Should make this optional (could use 
        info_main('# Biglinking object files')
        biglink(ctx, arch)

        # 5) postbuild packages
        info_main('# Postbuilding recipes')
        for recipe in recipes:
            info_main('Postbuilding {} for {}'.format(recipe.name, arch.arch))
            recipe.postbuild_arch(arch)

    info_main('# Installing pure Python modules')
    run_pymodules_install(ctx, python_modules)
    
    return

def run_pymodules_install(ctx, modules):
    if not modules:
        info('There are no Python modules to install, skipping')
        return
    info('The requirements ({}) don\'t have recipes, attempting to install '
         'them with pip'.format(', '.join(modules)))
    info('If this fails, it may mean that the module has compiled '
         'components and needs a recipe.')

    venv = sh.Command(ctx.virtualenv)
    with current_directory(join(ctx.build_dir)):
        shprint(venv, '--python=python2.7', 'venv')

        info('Creating a requirements.txt file for the Python modules')
        with open('requirements.txt', 'w') as fileh:
            for module in modules:
                fileh.write('{}\n'.format(module))

        info('Installing Python modules with pip')

        # AND: This doesn't work yet
        shprint(sh.bash, '-c', '''"source venv/bin/activate && env CC=/bin/false CXX=/bin/false pip install --target '{}' -r requirements.txt"'''.format(ctx.get_site_packages_dir()))
            

    
        

def biglink(ctx, arch):
    # First, collate object files from each recipe
    info('Collating object files from each recipe')
    obj_dir = join(ctx.bootstrap.build_dir, 'collated_objects')
    ensure_dir(obj_dir)
    recipes = [Recipe.get_recipe(name, ctx) for name in ctx.recipe_build_order]
    for recipe in recipes:
        recipe_obj_dir = join(recipe.get_build_container_dir(arch.arch),
                              'objects_{}'.format(recipe.name))
        if not exists(recipe_obj_dir):
            info('{} recipe has no biglinkable files dir, skipping'.format(recipe.name))
            continue
        files = glob.glob(join(recipe_obj_dir, '*'))
        if not len(files):
            info('{} recipe has no biglinkable files, skipping'.format(recipe.name))
        info('{} recipe has object files, copying'.format(recipe.name))
        files.append(obj_dir)
        shprint(sh.cp, '-r', *files)
    
    # AND: Shouldn't hardcode ArchAndroid! In reality need separate
    # build dirs for each arch
    arch = ArchAndroid(ctx)
    env = ArchAndroid(ctx).get_env()
    env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
        join(ctx.bootstrap.build_dir, 'obj', 'local', 'armeabi'))

    if not len(glob.glob(join(obj_dir, '*'))):
        info('There seem to be no libraries to biglink, skipping.')
        return
    info('Biglinking')
    # bl = sh.Command(join(ctx.root_dir, 'tools', 'biglink'))
    print('ldflags are', env['LDFLAGS'])
    # shprint(bl, join(ctx.libs_dir, 'libpymodules.so'),
    #         env['LIBLINK_PATH'], _env=env)
    biglink_function(
        join(ctx.libs_dir, 'libpymodules.so'),
        obj_dir.split(' '),
        # env['LIBLINK_PATH'].split(' '),  # AND: This line should be obselete now
        extra_link_dirs=[join(ctx.bootstrap.build_dir, 'obj', 'local', 'armeabi')],
        env=env)

def biglink_function(soname, objs_paths, extra_link_dirs=[], env=None):
    print('objs_paths are', objs_paths)
    sofiles = []

    for directory in objs_paths:
        for fn in os.listdir(directory):
            fn = os.path.join(directory, fn)

            if not fn.endswith(".so.o"):
                continue
            if not os.path.exists(fn[:-2] + ".libs"):
                continue

            sofiles.append(fn[:-2])

    # The raw argument list.
    args = [ ]

    for fn in sofiles:
        afn = fn + ".o"
        libsfn = fn + ".libs"

        args.append(afn)
        with open(libsfn) as fd:
            data = fd.read()
            args.extend(data.split(" "))

    unique_args = [ ]
    while args:
        a = args.pop()
        if a in ('-L', ):
            continue
        if a not in unique_args:
            unique_args.insert(0, a)

    for dir in extra_link_dirs:
        link = '-L{}'.format(dir)
        if link not in unique_args:
            unique_args.append(link)
    
    # print('Biglink create %s library' % soname)
    # print('Biglink arguments:')
    # for arg in unique_args:
    #     print(' %s' % arg)

    cc_name = env['CC']
    cc = sh.Command(cc_name.split()[0])
    cc = cc.bake(*cc_name.split()[1:])

    shprint(cc, '-shared', '-O3', '-o', soname, *unique_args, _env=env)
    # args = os.environ['CC'].split() + \
    #     ['-shared', '-O3', '-o', soname] + \
    #     unique_args

    # sys.exit(subprocess.call(args))



def ensure_dir(filename):
    if not exists(filename):
        makedirs(filename)

def dist_from_args(ctx, dist_args):
    '''Parses out any distribution-related arguments, and uses them to
    obtain a Distribution class instance for the build.
    '''
    return Distribution.get_distribution(
        ctx,
        name=dist_args.dist_name,
        recipes=split_argument_list(dist_args.requirements),
        allow_download=dist_args.allow_download,
        allow_build=dist_args.allow_build,
        extra_dist_dirs=split_argument_list(dist_args.extra_dist_dirs),
        require_perfect_match=dist_args.require_perfect_match)

def build_dist_from_args(ctx, dist, args_list):
    '''Parses out any bootstrap related arguments, and uses them to build
    a dist.'''
    parser = argparse.ArgumentParser(
        description='Create a newAndroid project')
    parser.add_argument('--bootstrap', help=('The name of the bootstrap type, \'pygame\' '
                                           'or \'sdl2\''))
    args, unknown = parser.parse_known_args(args_list)

    bs = Bootstrap.get_bootstrap(args.bootstrap, ctx)
    info_main('# Creating dist with with {} bootstrap'.format(bs.name))
    bs.distribution = dist
    info('Dist will have name {} and recipes ({})'.format(
        dist.name, ', '.join(dist.recipes)))

    ctx.dist_name = bs.distribution.name
    ctx.prepare_bootstrap(bs)
    ctx.prepare_dist(ctx.dist_name)

    recipes = dist.recipes
    build_recipes(recipes, ctx)

    ctx.bootstrap.run_distribute()

    info_main('# Your distribution was created successfully, exiting.')
    info('Dist can be found at (for now) {}'.format(join(ctx.dist_dir, ctx.dist_name)))

    return unknown


def split_argument_list(l):
    if not len(l):
        return []
    return re.split(r'[ ,]*', l)


# def create_dist

class ToolchainCL(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
                description="Tool for managing the iOS / Python toolchain",
                usage="""toolchain <command> [<args>]

Currently available commands:
create    Build an android project with all recipes

Available commands:
Not yet confirmed

Planned commands:
recipes
distributions
build_dist
symlink_dist
copy_dist
clean_all
status
clean_builds
clean_download_cache
clean_dists
""")
        parser.add_argument("command", help="Command to run")
        parser.add_argument('--debug', dest='debug', action='store_true',
                            help='Display debug output and all build info')

        # Options for specifying the Distribution
        parser.add_argument(
            '--dist_name', help='The name of the distribution to use or create',
            default='')
        parser.add_argument(
            '--requirements',
            help='Dependencies of your app, should be recipe names or Python modules',
            default='')
        parser.add_argument(
            '--allow_download', help='Allow binary dist download.',
            default=False, type=bool)
        parser.add_argument(
            '--allow_build', help='Allow compilation of a new distribution.',
            default=True, type=bool)
        parser.add_argument(
            '--force_build', help='Force compilation of a new distribution.',
            default=False, type=bool)
        parser.add_argument(
            '--extra_dist_dirs', help='Directories in which to look for distributions',
            default='')
        parser.add_argument(
            '--require_perfect_match', help=('Whether the dist recipes must '
                                             'perfectly match those requested.'),
            type=bool, default=False)

        
        args, unknown = parser.parse_known_args(sys.argv[1:])
        self.dist_args = args
        self.ctx = Context()
        
        if args.debug:
            logger.setLevel(logging.DEBUG)

        # import ipdb
        # ipdb.set_trace()
        # AND: Fail nicely if the args aren't handled yet
        if args.extra_dist_dirs:
            warning('Received --extra_dist_dirs but this arg currently is not '
                    'handled, exiting.')
            exit(1)
        if args.allow_download:
            warning('Received --allow_download but this arg currently is not '
                    'handled, exiting.')
            exit(1)
        # if args.allow_build:
        #     warning('Received --allow_build but this arg currently is not '
        #             'handled, exiting.')
        #     exit(1)
            
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)(unknown)

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

    def recipes(self, args):
        parser = argparse.ArgumentParser(
                description="List all the available recipes")
        parser.add_argument(
                "--compact", action="store_true",
                help="Produce a compact list suitable for scripting")
        parser.add_argument(
            '--color', type=bool, default=True,
            help='Whether the output should be coloured')
        args = parser.parse_args(args)

        if args.compact:
            print(" ".join(list(Recipe.list_recipes())))
        else:
            ctx = Context()
            for name in Recipe.list_recipes():
                recipe = Recipe.get_recipe(name, ctx)
                if args.color:
                    print('{Fore.BLUE}{Style.BRIGHT}{recipe.name:<12} '
                          '{Style.RESET_ALL}{Fore.LIGHTBLUE_EX}'
                          '{recipe.version:<8}{Style.RESET_ALL}'.format(
                          recipe=recipe, Fore=Fore, Style=Style))
                    print('    {Fore.GREEN}depends: {recipe.depends}'
                          '{Fore.RESET}'.format(recipe=recipe, Fore=Fore))
                    print('    {Fore.RED}conflicts: {recipe.conflicts}'
                          '{Fore.RESET}'.format(recipe=recipe, Fore=Fore))
                else:
                    print("{recipe.name:<12} {recipe.version:<8}".format(
                          recipe=recipe))
                    print('    depends: {recipe.depends}'.format(recipe=recipe))
                    print('    conflicts: {recipe.conflicts}'.format(recipe=recipe))

    def bootstraps(self, args):
        '''List all the bootstraps available to build with.'''
        print(list(Bootstrap.list_bootstraps()))

    def clean_all(self, args):
        '''Delete all build components; the package cache, package builds,
        bootstrap builds and distributions.'''
        parser = argparse.ArgumentParser(
                description="Clean the build cache, downloads and dists")
        args = parser.parse_args(args)
        ctx = Context()
        if exists(ctx.build_dir):
            shutil.rmtree(ctx.build_dir)
        if exists(ctx.dist_dir):
            shutil.rmtree(ctx.dist_dir)
        if exists(ctx.packages_path):
            shutil.rmtree(ctx.packages_path)

    def clean_dists(self, args):
        '''Delete all compiled distributions in the internal distribution
        directory.'''
        parser = argparse.ArgumentParser(
                description="Delete any distributions that have been built.")
        args = parser.parse_args(args)
        ctx = Context()
        if exists(ctx.dist_dir):
            shutil.rmtree(ctx.dist_dir)

    def clean_builds(self, args):
        '''Delete all build caches for each recipe.

        This does *not* delete the package download cache or the final distributions.
        '''
        parser = argparse.ArgumentParser(
                description="Delete all build files (but not download caches)")
        args = parser.parse_args(args)
        ctx = Context()
        if exists(ctx.dist_dir):
            shutil.rmtree(ctx.dist_dir)
        if exists(ctx.build_dir):
            shutil.rmtree(ctx.build_dir)

    def clean_download_cache(self, args):
        '''
        Deletes any downloaded recipe packages.

        This does *not* delete the build caches or final distributions.
        '''
        parser = argparse.ArgumentParser(
                description="Delete all download caches")
        args = parser.parse_args(args)
        ctx = Context()
        if exists(ctx.packages_path):
            shutil.rmtree(ctx.packages_path)

    # def status(self, args):
    #     parser = argparse.ArgumentParser(
    #             description="Give a status of the build")
    #     args = parser.parse_args(args)
    #     ctx = Context()
    #     # AND: TODO

    #     print('This isn\'t implemented yet, but should list all currently existing '
    #           'distributions, the modules they include, and all the build caches.')
    #     exit(1)

    @require_prebuilt_dist
    def export_dist(self, args):
        '''Copies a created dist to an output dir.

        This makes it easy to navigate to the dist to investigate it
        or call build.py, though you do not in general need to do this
        and can use the apk command instead.
        '''
        parser = argparse.ArgumentParser(
            description='Copy a created dist to a given directory')
        parser.add_argument('--output', help=('The output dir to copy to'),
                            required=True)
        args = parser.parse_args(args)

        ctx = self.ctx
        dist = dist_from_args(ctx, self.dist_args)
        if dist.needs_build:
            info('You asked to export a dist, but there is no dist with suitable '
                 'recipes available. For now, you must create one first with '
                 'the create argument.')
            exit(1)
        shprint(sh.cp, '-r', dist.dist_dir, args.output)

    @require_prebuilt_dist
    def symlink_dist(self, args):
        '''Symlinks a created dist to an output dir.

        This makes it easy to navigate to the dist to investigate it
        or call build.py, though you do not in general need to do this
        and can use the apk command instead.

        '''
        parser = argparse.ArgumentParser(
            description='Symlink a created dist to a given directory')
        parser.add_argument('--output', help=('The output dir to copy to'),
                            required=True)
        args = parser.parse_args(args)

        ctx = self.ctx
        dist = dist_from_args(ctx, self.dist_args)
        if dist.needs_build:
            info('You asked to symlink a dist, but there is no dist with suitable '
                 'recipes available. For now, you must create one first with '
                 'the create argument.')
            exit(1)
        shprint(sh.ln, '-s', dist.dist_dir, args.output)

    # def _get_dist(self):
    #     ctx = self.ctx
    #     dist = dist_from_args(ctx, self.dist_args)

    @property
    def dist(self):
        ctx = self.ctx
        dist = dist_from_args(ctx, self.dist_args)
        return dist

    @require_prebuilt_dist
    def apk(self, args):
        '''Create an APK using the given distribution.'''

        # AND: Need to add a parser here for any extra options
        # parser = argparse.ArgumentParser(
        #     description='Build an APK')
        # args = parser.parse_args(args)

        ctx = self.ctx
        # dist = dist_from_args(ctx, self.dist_args)
        # if dist.needs_build:
        #     info('No dist exists that meets your requirements, so one will '
        #          'be built.')
        #     args = build_dist_from_args(ctx, dist, args)

        build = imp.load_source('build', join(dist.dist_dir, 'build.py'))
        with current_directory(dist.dist_dir):
            build.parse_args(args)

            shprint(sh.ant, 'debug')

        # AND: This is very crude, needs improving. Also only works
        # for debug for now.

        info_main('# Copying APK to current directory')
        apks = glob.glob(join(dist.dist_dir, 'bin', '*-*-debug.apk'))
        if len(apks) == 0:
            raise ValueError('Couldn\'t find the built APK')
        if len(apks) > 1:
            info('More than one built APK found...guessing you '
                 'just built {}'.format(apks[-1]))
        shprint(sh.cp, apks[-1], './')
        

    @require_prebuilt_dist
    def create(self, args):
        '''Create a distribution directory if it doesn't already exist, run
        any recipes if necessary, and build the apk.
        '''
        pass  # The decorator does this for us
        # ctx = self.ctx

        # dist = dist_from_args(ctx, self.dist_args)
        # if not dist.needs_build:
        #     info('You asked to create a distribution, but a dist with this name '
        #          'already exists. If you don\'t want to use '
        #          'it, you must delete it and rebuild, or create your '
        #          'new dist with a different name.')
        #     exit(1)
        # info('Ready to create dist {}, contains recipes {}'.format(
        #     dist.name, ', '.join(dist.recipes)))

        # build_dist_from_args(ctx, dist, args)

    def print_context_info(self, args):
        '''Prints some debug information about which system paths
        python-for-android will internally use for package building, along
        with information about where the Android SDK and NDK will be called
        from.'''
        ctx = Context()
        for attribute in ('root_dir', 'build_dir', 'dist_dir', 'libs_dir',
                          'ccache', 'cython', 'sdk_dir', 'ndk_dir', 'ndk_platform',
                          'ndk_ver', 'android_api'):
            print('{} is {}'.format(attribute, getattr(ctx, attribute)))

    def distributions(self, args):
        '''Lists all distributions currently available (i.e. that have already
        been built).'''
        ctx = Context()
        dists = Distribution.get_distributions(ctx)

        infos = []
        for dist in dists:
            infos.append('{Fore.GREEN}{Style.BRIGHT}{name}{Style.RESET_ALL}: '
                         'includes recipes ({Fore.GREEN}{recipes}'
                         '{Style.RESET_ALL})'.format(
                             name=dist.name, recipes=', '.join(dist.recipes),
                             Fore=Fore, Style=Style))
            
        print('{Style.BRIGHT}Distributions stored internally are:'
              '{Style.RESET_ALL}'.format(Style=Style, Fore=Fore))
        for line in infos:
            print('\t' + line)
        
def test_setuptools_entry(*args, **kwargs):
    print('args are', args)
    print('kwargs are', kwargs)

if __name__ == "__main__":

    ToolchainCL()
