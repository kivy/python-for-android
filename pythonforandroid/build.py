from __future__ import print_function

from os.path import (join, realpath, dirname, expanduser, exists,
                     split, isdir)
from os import environ
import os
import glob
import sys
import re
import sh

from pythonforandroid.util import (ensure_dir, current_directory)
from pythonforandroid.logger import (info, warning, error, info_notify,
                                     Err_Fore, info_main, shprint)
from pythonforandroid.archs import ArchARM, ArchARMv7_a, ArchAarch_64, Archx86
from pythonforandroid.recipe import Recipe

DEFAULT_ANDROID_API = 15


class Context(object):
    '''A build context. If anything will be built, an instance this class
    will be instantiated and used to hold all the build state.'''

    env = environ.copy()
    # the filepath of toolchain.py
    root_dir = None
    # the root dir where builds and dists will be stored
    storage_dir = None

    # in which bootstraps are copied for building
    # and recipes are built
    build_dir = None
    # the Android project folder where everything ends up
    dist_dir = None
    # where Android libs are cached after build
    # but before being placed in dists
    libs_dir = None
    aars_dir = None

    ccache = None  # whether to use ccache
    cython = None  # the cython interpreter name

    ndk_platform = None  # the ndk platform directory

    dist_name = None  # should be deprecated in favour of self.dist.dist_name
    bootstrap = None
    bootstrap_build_dir = None

    recipe_build_order = None  # Will hold the list of all built recipes

    symlink_java_src = False  # If True, will symlink instead of copying during build

    java_build_tool = 'auto'

    @property
    def packages_path(self):
        '''Where packages are downloaded before being unpacked'''
        return join(self.storage_dir, 'packages')

    @property
    def templates_dir(self):
        return join(self.root_dir, 'templates')

    @property
    def libs_dir(self):
        # Was previously hardcoded as self.build_dir/libs
        dir = join(self.build_dir, 'libs_collections',
                   self.bootstrap.distribution.name)
        ensure_dir(dir)
        return dir

    @property
    def javaclass_dir(self):
        # Was previously hardcoded as self.build_dir/java
        dir = join(self.build_dir, 'javaclasses',
                   self.bootstrap.distribution.name)
        ensure_dir(dir)
        return dir

    @property
    def aars_dir(self):
        dir = join(self.build_dir, 'aars', self.bootstrap.distribution.name)
        ensure_dir(dir)
        return dir

    @property
    def python_installs_dir(self):
        dir = join(self.build_dir, 'python-installs')
        ensure_dir(dir)
        return dir

    def get_python_install_dir(self):
        dir = join(self.python_installs_dir, self.bootstrap.distribution.name)
        return dir

    def setup_dirs(self, storage_dir):
        '''Calculates all the storage and build dirs, and makes sure
        the directories exist where necessary.'''
        self.storage_dir = expanduser(storage_dir)
        if ' ' in self.storage_dir:
            raise ValueError('storage dir path cannot contain spaces, please '
                             'specify a path with --storage-dir')
        self.build_dir = join(self.storage_dir, 'build')
        self.dist_dir = join(self.storage_dir, 'dists')

    def ensure_dirs(self):
        ensure_dir(self.storage_dir)
        ensure_dir(self.build_dir)
        ensure_dir(self.dist_dir)
        ensure_dir(join(self.build_dir, 'bootstrap_builds'))
        ensure_dir(join(self.build_dir, 'other_builds'))

    @property
    def android_api(self):
        '''The Android API being targeted.'''
        if self._android_api is None:
            raise ValueError('Tried to access android_api but it has not '
                             'been set - this should not happen, something '
                             'went wrong!')
        return self._android_api

    @android_api.setter
    def android_api(self, value):
        self._android_api = value

    @property
    def ndk_ver(self):
        '''The version of the NDK being used for compilation.'''
        if self._ndk_ver is None:
            raise ValueError('Tried to access ndk_ver but it has not '
                             'been set - this should not happen, something '
                             'went wrong!')
        return self._ndk_ver

    @ndk_ver.setter
    def ndk_ver(self, value):
        self._ndk_ver = value

    @property
    def sdk_dir(self):
        '''The path to the Android SDK.'''
        if self._sdk_dir is None:
            raise ValueError('Tried to access sdk_dir but it has not '
                             'been set - this should not happen, something '
                             'went wrong!')
        return self._sdk_dir

    @sdk_dir.setter
    def sdk_dir(self, value):
        self._sdk_dir = value

    @property
    def ndk_dir(self):
        '''The path to the Android NDK.'''
        if self._ndk_dir is None:
            raise ValueError('Tried to access ndk_dir but it has not '
                             'been set - this should not happen, something '
                             'went wrong!')
        return self._ndk_dir

    @ndk_dir.setter
    def ndk_dir(self, value):
        self._ndk_dir = value

    def prepare_build_environment(self, user_sdk_dir, user_ndk_dir,
                                  user_android_api, user_ndk_ver):
        '''Checks that build dependencies exist and sets internal variables
        for the Android SDK etc.

        ..warning:: This *must* be called before trying any build stuff

        '''

        self.ensure_dirs()

        if self._build_env_prepared:
            return

        ok = True

        # Work out where the Android SDK is
        sdk_dir = None
        if user_sdk_dir:
            sdk_dir = user_sdk_dir
        # This is the old P4A-specific var
        if sdk_dir is None:
            sdk_dir = environ.get('ANDROIDSDK', None)
        # This seems used more conventionally
        if sdk_dir is None:
            sdk_dir = environ.get('ANDROID_HOME', None)
        # Checks in the buildozer SDK dir, useful for debug tests of p4a
        if sdk_dir is None:
            possible_dirs = glob.glob(expanduser(join(
                '~', '.buildozer', 'android', 'platform', 'android-sdk-*')))
            possible_dirs = [d for d in possible_dirs if not
                             (d.endswith('.bz2') or d.endswith('.gz'))]
            if possible_dirs:
                info('Found possible SDK dirs in buildozer dir: {}'.format(
                    ', '.join([d.split(os.sep)[-1] for d in possible_dirs])))
                info('Will attempt to use SDK at {}'.format(possible_dirs[0]))
                warning('This SDK lookup is intended for debug only, if you '
                        'use python-for-android much you should probably '
                        'maintain your own SDK download.')
                sdk_dir = possible_dirs[0]
        if sdk_dir is None:
            warning('Android SDK dir was not specified, exiting.')
            exit(1)
        self.sdk_dir = realpath(sdk_dir)

        # Check what Android API we're using
        android_api = None
        if user_android_api:
            android_api = user_android_api
            if android_api is not None:
                info('Getting Android API version from user argument')
        if android_api is None:
            android_api = environ.get('ANDROIDAPI', None)
            if android_api is not None:
                info('Found Android API target in $ANDROIDAPI:'
                     ' it is {}'.format(android_api))
        if android_api is None:
            info('Android API target was not set manually, using '
                 'the default of {}'.format(DEFAULT_ANDROID_API))
            android_api = DEFAULT_ANDROID_API
        android_api = int(android_api)
        self.android_api = android_api

        if self.android_api >= 21 and self.archs[0].arch == 'armeabi':
            error('Asked to build for armeabi architecture with API '
                  '{}, but API 21 or greater does not support armeabi'.format(
                      self.android_api))
            error('You probably want to build with --arch=armeabi-v7a instead')
            exit(1)

        if exists(join(sdk_dir, 'tools', 'bin', 'avdmanager')):
            avdmanager = sh.Command(join(sdk_dir, 'tools', 'bin', 'avdmanager'))
            targets = avdmanager('list', 'target').stdout.decode('utf-8').split('\n')
        elif exists(join(sdk_dir, 'tools', 'android')):
            android = sh.Command(join(sdk_dir, 'tools', 'android'))
            targets = android('list').stdout.decode('utf-8').split('\n')
        else:
            error('Could not find `android` or `sdkmanager` binaries in '
                  'Android SDK. Exiting.')
            exit(1)
        apis = [s for s in targets if re.match(r'^ *API level: ', s)]
        apis = [re.findall(r'[0-9]+', s) for s in apis]
        apis = [int(s[0]) for s in apis if s]
        info('Available Android APIs are ({})'.format(
            ', '.join(map(str, apis))))
        if android_api in apis:
            info(('Requested API target {} is available, '
                  'continuing.').format(android_api))
        else:
            warning(('Requested API target {} is not available, install '
                     'it with the SDK android tool.').format(android_api))
            warning('Exiting.')
            exit(1)

        # Find the Android NDK
        # Could also use ANDROID_NDK, but doesn't look like many tools use this
        ndk_dir = None
        if user_ndk_dir:
            ndk_dir = user_ndk_dir
            if ndk_dir is not None:
                info('Getting NDK dir from from user argument')
        if ndk_dir is None:  # The old P4A-specific dir
            ndk_dir = environ.get('ANDROIDNDK', None)
            if ndk_dir is not None:
                info('Found NDK dir in $ANDROIDNDK:'
                     ' it is {}'.format(ndk_dir))
        if ndk_dir is None:  # Apparently the most common convention
            ndk_dir = environ.get('NDK_HOME', None)
            if ndk_dir is not None:
                info('Found NDK dir in $NDK_HOME:'
                     ' it is {}'.format(ndk_dir))
        if ndk_dir is None:  # Another convention (with maven?)
            ndk_dir = environ.get('ANDROID_NDK_HOME', None)
            if ndk_dir is not None:
                info('Found NDK dir in $ANDROID_NDK_HOME:'
                     ' it is {}'.format(ndk_dir))
        if ndk_dir is None:  # Checks in the buildozer NDK dir, useful
            #                # for debug tests of p4a
            possible_dirs = glob.glob(expanduser(join(
                '~', '.buildozer', 'android', 'platform', 'android-ndk-r*')))
            if possible_dirs:
                info('Found possible NDK dirs in buildozer dir: {}'.format(
                    ', '.join([d.split(os.sep)[-1] for d in possible_dirs])))
                info('Will attempt to use NDK at {}'.format(possible_dirs[0]))
                warning('This NDK lookup is intended for debug only, if you '
                        'use python-for-android much you should probably '
                        'maintain your own NDK download.')
                ndk_dir = possible_dirs[0]
        if ndk_dir is None:
            warning('Android NDK dir was not specified, exiting.')
            exit(1)
        self.ndk_dir = realpath(ndk_dir)

        # Find the NDK version, and check it against what the NDK dir
        # seems to report
        ndk_ver = None
        if user_ndk_ver:
            ndk_ver = user_ndk_ver
            if ndk_dir is not None:
                info('Got NDK version from from user argument:'
                     ' it is {}'.format(ndk_ver))
        if ndk_ver is None:
            ndk_ver = environ.get('ANDROIDNDKVER', None)
            if ndk_dir is not None:
                info('Got NDK version from $ANDROIDNDKVER:'
                     ' it is {}'.format(ndk_ver))

        self.ndk = 'google'

        try:
            with open(join(ndk_dir, 'RELEASE.TXT')) as fileh:
                reported_ndk_ver = fileh.read().split(' ')[0].strip()
        except IOError:
            pass
        else:
            if reported_ndk_ver.startswith('crystax-ndk-'):
                reported_ndk_ver = reported_ndk_ver[12:]
                self.ndk = 'crystax'
            if ndk_ver is None:
                ndk_ver = reported_ndk_ver
                info(('Got Android NDK version from the NDK dir: '
                      'it is {}').format(ndk_ver))
            else:
                if ndk_ver != reported_ndk_ver:
                    warning('NDK version was set as {}, but checking '
                            'the NDK dir claims it is {}.'.format(
                                ndk_ver, reported_ndk_ver))
                    warning('The build will try to continue, but it may '
                            'fail and you should check '
                            'that your setting is correct.')
                    warning('If the NDK dir result is correct, you don\'t '
                            'need to manually set the NDK ver.')
        if ndk_ver is None:
            warning('Android NDK version could not be found. This probably'
                    'won\'t cause any problems, but if necessary you can'
                    'set it with `--ndk-version=...`.')
        self.ndk_ver = ndk_ver

        info('Using {} NDK {}'.format(self.ndk.capitalize(), self.ndk_ver))

        virtualenv = None
        if virtualenv is None:
            virtualenv = sh.which('virtualenv2')
        if virtualenv is None:
            virtualenv = sh.which('virtualenv-2.7')
        if virtualenv is None:
            virtualenv = sh.which('virtualenv')
        if virtualenv is None:
            raise IOError('Couldn\'t find a virtualenv executable, '
                          'you must install this to use p4a.')
        self.virtualenv = virtualenv
        info('Found virtualenv at {}'.format(virtualenv))

        # path to some tools
        self.ccache = sh.which("ccache")
        if not self.ccache:
            info('ccache is missing, the build will not be optimized in the '
                 'future.')
        for cython_fn in ("cython2", "cython-2.7", "cython"):
            cython = sh.which(cython_fn)
            if cython:
                self.cython = cython
                break
        else:
            error('No cython binary found. Exiting.')
            exit(1)
        if not self.cython:
            ok = False
            warning("Missing requirement: cython is not installed")

        # This would need to be changed if supporting multiarch APKs
        arch = self.archs[0]
        platform_dir = arch.platform_dir
        toolchain_prefix = arch.toolchain_prefix
        toolchain_version = None
        self.ndk_platform = join(
            self.ndk_dir,
            'platforms',
            'android-{}'.format(self.android_api),
            platform_dir)
        if not exists(self.ndk_platform):
            warning('ndk_platform doesn\'t exist: {}'.format(
                self.ndk_platform))
            ok = False

        py_platform = sys.platform
        if py_platform in ['linux2', 'linux3']:
            py_platform = 'linux'

        toolchain_versions = []
        toolchain_path = join(self.ndk_dir, 'toolchains')
        if isdir(toolchain_path):
            toolchain_contents = glob.glob('{}/{}-*'.format(toolchain_path,
                                                            toolchain_prefix))
            toolchain_versions = [split(path)[-1][len(toolchain_prefix) + 1:]
                                  for path in toolchain_contents]
        else:
            warning('Could not find toolchain subdirectory!')
            ok = False
        toolchain_versions.sort()

        toolchain_versions_gcc = []
        for toolchain_version in toolchain_versions:
            if toolchain_version[0].isdigit():
                # GCC toolchains begin with a number
                toolchain_versions_gcc.append(toolchain_version)

        if toolchain_versions:
            info('Found the following toolchain versions: {}'.format(
                toolchain_versions))
            info('Picking the latest gcc toolchain, here {}'.format(
                toolchain_versions_gcc[-1]))
            toolchain_version = toolchain_versions_gcc[-1]
        else:
            warning('Could not find any toolchain for {}!'.format(
                toolchain_prefix))
            ok = False

        self.toolchain_prefix = toolchain_prefix
        self.toolchain_version = toolchain_version
        # Modify the path so that sh finds modules appropriately
        environ['PATH'] = (
            '{ndk_dir}/toolchains/{toolchain_prefix}-{toolchain_version}/'
            'prebuilt/{py_platform}-x86/bin/:{ndk_dir}/toolchains/'
            '{toolchain_prefix}-{toolchain_version}/prebuilt/'
            '{py_platform}-x86_64/bin/:{ndk_dir}:{sdk_dir}/'
            'tools:{path}').format(
                sdk_dir=self.sdk_dir, ndk_dir=self.ndk_dir,
                toolchain_prefix=toolchain_prefix,
                toolchain_version=toolchain_version,
                py_platform=py_platform, path=environ.get('PATH'))

        for executable in ("pkg-config", "autoconf", "automake", "libtoolize",
                           "tar", "bzip2", "unzip", "make", "gcc", "g++"):
            if not sh.which(executable):
                warning("Missing executable: {} is not installed".format(
                    executable))

        if not ok:
            error('{}python-for-android cannot continue; aborting{}'.format(
                Err_Fore.RED, Err_Fore.RESET))
            sys.exit(1)

    def __init__(self):
        super(Context, self).__init__()
        self.include_dirs = []

        self._build_env_prepared = False

        self._sdk_dir = None
        self._ndk_dir = None
        self._android_api = None
        self._ndk_ver = None
        self.ndk = None

        self.toolchain_prefix = None
        self.toolchain_version = None

        self.local_recipes = None
        self.copy_libs = False

        # this list should contain all Archs, it is pruned later
        self.archs = (
            ArchARM(self),
            ArchARMv7_a(self),
            Archx86(self),
            ArchAarch_64(self),
            )

        self.root_dir = realpath(dirname(__file__))

        # remove the most obvious flags that can break the compilation
        self.env.pop("LDFLAGS", None)
        self.env.pop("ARCHFLAGS", None)
        self.env.pop("CFLAGS", None)

        self.python_recipe = None  # Set by TargetPythonRecipe

    def set_archs(self, arch_names):
        all_archs = self.archs
        new_archs = set()
        for name in arch_names:
            matching = [arch for arch in all_archs if arch.arch == name]
            for match in matching:
                new_archs.add(match)
        self.archs = list(new_archs)
        if not self.archs:
            warning('Asked to compile for no Archs, so failing.')
            exit(1)
        info('Will compile for the following archs: {}'.format(
            ', '.join([arch.arch for arch in self.archs])))

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

        # This needs to be replaced with something more general in
        # order to support multiple python versions and/or multiple
        # archs.
        if self.python_recipe.from_crystax:
            return self.get_python_install_dir()
        return join(self.get_python_install_dir(),
                    'lib', 'python2.7', 'site-packages')

    def get_libs_dir(self, arch):
        '''The libs dir for a given arch.'''
        ensure_dir(join(self.libs_dir, arch))
        return join(self.libs_dir, arch)

    def has_lib(self, arch, lib):
        return exists(join(self.get_libs_dir(arch), lib))

    def has_package(self, name, arch=None):
        try:
            recipe = Recipe.get_recipe(name, self)
        except IOError:
            pass
        else:
            name = getattr(recipe, 'site_packages_name', None) or name
        name = name.replace('.', '/')
        site_packages_dir = self.get_site_packages_dir(arch)
        return (exists(join(site_packages_dir, name)) or
                exists(join(site_packages_dir, name + '.py')) or
                exists(join(site_packages_dir, name + '.pyc')) or
                exists(join(site_packages_dir, name + '.pyo')) or
                exists(join(site_packages_dir, name + '.so')) or
                glob.glob(join(site_packages_dir, name + '-*.egg')))

    def not_has_package(self, name, arch=None):
        return not self.has_package(name, arch)


def build_recipes(build_order, python_modules, ctx):
    # Put recipes in correct build order
    bs = ctx.bootstrap
    info_notify("Recipe build order is {}".format(build_order))
    if python_modules:
        python_modules = sorted(set(python_modules))
        info_notify(
            ('The requirements ({}) were not found as recipes, they will be '
             'installed with pip.').format(', '.join(python_modules)))

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
            recipe.apply_patches(arch)

        # 3) build packages
        info_main('# Building recipes')
        for recipe in recipes:
            info_main('Building {} for {}'.format(recipe.name, arch.arch))
            if recipe.should_build(arch):
                recipe.build_arch(arch)
            else:
                info('{} said it is already built, skipping'
                     .format(recipe.name))

        # 4) biglink everything
        info_main('# Biglinking object files')
        if not ctx.python_recipe or not ctx.python_recipe.from_crystax:
            biglink(ctx, arch)
        else:
            info('NDK is crystax, skipping biglink (will this work?)')

        # 5) postbuild packages
        info_main('# Postbuilding recipes')
        for recipe in recipes:
            info_main('Postbuilding {} for {}'.format(recipe.name, arch.arch))
            recipe.postbuild_arch(arch)

    info_main('# Installing pure Python modules')
    run_pymodules_install(ctx, python_modules)

    return


def run_pymodules_install(ctx, modules):
    modules = list(filter(ctx.not_has_package, modules))

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
                key = 'VERSION_' + module
                if key in environ:
                    line = '{}=={}\n'.format(module, environ[key])
                else:
                    line = '{}\n'.format(module)
                fileh.write(line)

        info('Installing Python modules with pip')
        info('If this fails with a message about /bin/false, this '
             'probably means the package cannot be installed with '
             'pip as it needs a compilation recipe.')

        # This bash method is what old-p4a used
        # It works but should be replaced with something better
        shprint(sh.bash, '-c', (
            "source venv/bin/activate && env CC=/bin/false CXX=/bin/false "
            "PYTHONPATH={0} pip install --target '{0}' --no-deps -r requirements.txt"
        ).format(ctx.get_site_packages_dir()))


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
            info('{} recipe has no biglinkable files dir, skipping'
                 .format(recipe.name))
            continue
        files = glob.glob(join(recipe_obj_dir, '*'))
        if not len(files):
            info('{} recipe has no biglinkable files, skipping'
                 .format(recipe.name))
            continue
        info('{} recipe has object files, copying'.format(recipe.name))
        files.append(obj_dir)
        shprint(sh.cp, '-r', *files)

    env = arch.get_env()
    env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
        join(ctx.bootstrap.build_dir, 'obj', 'local', arch.arch))

    if not len(glob.glob(join(obj_dir, '*'))):
        info('There seem to be no libraries to biglink, skipping.')
        return
    info('Biglinking')
    info('target {}'.format(join(ctx.get_libs_dir(arch.arch),
                                 'libpymodules.so')))
    do_biglink = copylibs_function if ctx.copy_libs else biglink_function

    # Move to the directory containing crtstart_so.o and crtend_so.o
    # This is necessary with newer NDKs? A gcc bug?
    with current_directory(join(ctx.ndk_platform, 'usr', 'lib')):
        do_biglink(
            join(ctx.get_libs_dir(arch.arch), 'libpymodules.so'),
            obj_dir.split(' '),
            extra_link_dirs=[join(ctx.bootstrap.build_dir,
                                  'obj', 'local', arch.arch),
                             os.path.abspath('.')],
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
    args = []

    for fn in sofiles:
        afn = fn + ".o"
        libsfn = fn + ".libs"

        args.append(afn)
        with open(libsfn) as fd:
            data = fd.read()
            args.extend(data.split(" "))

    unique_args = []
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

    cc_name = env['CC']
    cc = sh.Command(cc_name.split()[0])
    cc = cc.bake(*cc_name.split()[1:])

    shprint(cc, '-shared', '-O3', '-o', soname, *unique_args, _env=env)


def copylibs_function(soname, objs_paths, extra_link_dirs=[], env=None):
    print('objs_paths are', objs_paths)

    re_needso = re.compile(r'^.*\(NEEDED\)\s+Shared library: \[lib(.*)\.so\]\s*$')
    blacklist_libs = (
        'c',
        'stdc++',
        'dl',
        'python2.7',
        'sdl',
        'sdl_image',
        'sdl_ttf',
        'z',
        'm',
        'GLESv2',
        'jpeg',
        'png',
        'log',

        # bootstrap takes care of sdl2 libs (if applicable)
        'SDL2',
        'SDL2_ttf',
        'SDL2_image',
        'SDL2_mixer',
    )
    found_libs = []
    sofiles = []
    if env and 'READELF' in env:
        readelf = env['READELF']
    elif 'READELF' in os.environ:
        readelf = os.environ['READELF']
    else:
        readelf = sh.which('readelf').strip()
    readelf = sh.Command(readelf).bake('-d')

    dest = dirname(soname)

    for directory in objs_paths:
        for fn in os.listdir(directory):
            fn = join(directory, fn)

            if not fn.endswith('.libs'):
                continue

            dirfn = fn[:-1] + 'dirs'
            if not exists(dirfn):
                continue

            with open(fn) as f:
                libs = f.read().strip().split(' ')
                needed_libs = [lib for lib in libs
                               if lib and
                               lib not in blacklist_libs and
                               lib not in found_libs]

            while needed_libs:
                print('need libs:\n\t' + '\n\t'.join(needed_libs))

                start_needed_libs = needed_libs[:]
                found_sofiles = []

                with open(dirfn) as f:
                    libdirs = f.read().split()
                    for libdir in libdirs:
                        if not needed_libs:
                            break

                        if libdir == dest:
                            # don't need to copy from dest to dest!
                            continue

                        libdir = libdir.strip()
                        print('scanning', libdir)
                        for lib in needed_libs[:]:
                            if lib in found_libs:
                                continue

                            if lib.endswith('.a'):
                                needed_libs.remove(lib)
                                found_libs.append(lib)
                                continue

                            lib_a = 'lib' + lib + '.a'
                            libpath_a = join(libdir, lib_a)
                            lib_so = 'lib' + lib + '.so'
                            libpath_so = join(libdir, lib_so)
                            plain_so = lib + '.so'
                            plainpath_so = join(libdir, plain_so)

                            sopath = None
                            if exists(libpath_so):
                                sopath = libpath_so
                            elif exists(plainpath_so):
                                sopath = plainpath_so

                            if sopath:
                                print('found', lib, 'in', libdir)
                                found_sofiles.append(sopath)
                                needed_libs.remove(lib)
                                found_libs.append(lib)
                                continue

                            if exists(libpath_a):
                                print('found', lib, '(static) in', libdir)
                                needed_libs.remove(lib)
                                found_libs.append(lib)
                                continue

                for sofile in found_sofiles:
                    print('scanning dependencies for', sofile)
                    out = readelf(sofile)
                    for line in out.splitlines():
                        needso = re_needso.match(line)
                        if needso:
                            lib = needso.group(1)
                            if (lib not in needed_libs
                                    and lib not in found_libs
                                    and lib not in blacklist_libs):
                                needed_libs.append(needso.group(1))

                sofiles += found_sofiles

                if needed_libs == start_needed_libs:
                    raise RuntimeError(
                            'Failed to locate needed libraries!\n\t' +
                            '\n\t'.join(needed_libs))

    print('Copying libraries')
    for lib in sofiles:
        shprint(sh.cp, lib, dest)
