from os.path import (
    abspath, join, realpath, dirname, expanduser, exists,
    split, isdir
)
from os import environ
import copy
import os
import glob
import sys
import re
import sh
import shutil
import subprocess
from contextlib import suppress

from pythonforandroid.util import (
    current_directory, ensure_dir,
    BuildInterruptingException,
)
from pythonforandroid.logger import (info, warning, info_notify, info_main, shprint)
from pythonforandroid.archs import ArchARM, ArchARMv7_a, ArchAarch_64, Archx86, Archx86_64
from pythonforandroid.pythonpackage import get_package_name
from pythonforandroid.recipe import CythonRecipe, Recipe
from pythonforandroid.recommendations import (
    check_ndk_version, check_target_api, check_ndk_api,
    RECOMMENDED_NDK_API, RECOMMENDED_TARGET_API)


def get_ndk_platform_dir(ndk_dir, ndk_api, arch):
    ndk_platform_dir_exists = True
    platform_dir = arch.platform_dir
    ndk_platform = join(
        ndk_dir,
        'platforms',
        'android-{}'.format(ndk_api),
        platform_dir)
    if not exists(ndk_platform):
        warning("ndk_platform doesn't exist: {}".format(ndk_platform))
        ndk_platform_dir_exists = False
    return ndk_platform, ndk_platform_dir_exists


def get_toolchain_versions(ndk_dir, arch):
    toolchain_versions = []
    toolchain_path_exists = True
    toolchain_prefix = arch.toolchain_prefix
    toolchain_path = join(ndk_dir, 'toolchains')
    if isdir(toolchain_path):
        toolchain_contents = glob.glob('{}/{}-*'.format(toolchain_path,
                                                        toolchain_prefix))
        toolchain_versions = [split(path)[-1][len(toolchain_prefix) + 1:]
                              for path in toolchain_contents]
    else:
        warning('Could not find toolchain subdirectory!')
        toolchain_path_exists = False
    return toolchain_versions, toolchain_path_exists


def get_targets(sdk_dir):
    if exists(join(sdk_dir, 'tools', 'bin', 'avdmanager')):
        avdmanager = sh.Command(join(sdk_dir, 'tools', 'bin', 'avdmanager'))
        targets = avdmanager('list', 'target').stdout.decode('utf-8').split('\n')
    elif exists(join(sdk_dir, 'tools', 'android')):
        android = sh.Command(join(sdk_dir, 'tools', 'android'))
        targets = android('list').stdout.decode('utf-8').split('\n')
    else:
        raise BuildInterruptingException(
            'Could not find `android` or `sdkmanager` binaries in Android SDK',
            instructions='Make sure the path to the Android SDK is correct')
    return targets


def get_available_apis(sdk_dir):
    targets = get_targets(sdk_dir)
    apis = [s for s in targets if re.match(r'^ *API level: ', s)]
    apis = [re.findall(r'[0-9]+', s) for s in apis]
    apis = [int(s[0]) for s in apis if s]
    return apis


class Context:
    '''A build context. If anything will be built, an instance this class
    will be instantiated and used to hold all the build state.'''

    # Whether to make a debug or release build
    build_as_debuggable = False

    # Whether to strip debug symbols in `.so` files
    with_debug_symbols = False

    env = environ.copy()
    # the filepath of toolchain.py
    root_dir = None
    # the root dir where builds and dists will be stored
    storage_dir = None

    # in which bootstraps are copied for building
    # and recipes are built
    build_dir = None

    distribution = None
    """The Distribution object representing the current build target location."""

    # the Android project folder where everything ends up
    dist_dir = None

    # where Android libs are cached after build
    # but before being placed in dists
    libs_dir = None
    aars_dir = None

    # Whether setup.py or similar should be used if present:
    use_setup_py = False

    ccache = None  # whether to use ccache

    ndk_platform = None  # the ndk platform directory

    bootstrap = None
    bootstrap_build_dir = None

    recipe_build_order = None  # Will hold the list of all built recipes

    symlink_bootstrap_files = False  # If True, will symlink instead of copying during build

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
        directory = join(self.build_dir, 'libs_collections',
                         self.bootstrap.distribution.name)
        ensure_dir(directory)
        return directory

    @property
    def javaclass_dir(self):
        # Was previously hardcoded as self.build_dir/java
        directory = join(self.build_dir, 'javaclasses',
                         self.bootstrap.distribution.name)
        ensure_dir(directory)
        return directory

    @property
    def aars_dir(self):
        directory = join(self.build_dir, 'aars', self.bootstrap.distribution.name)
        ensure_dir(directory)
        return directory

    @property
    def python_installs_dir(self):
        directory = join(self.build_dir, 'python-installs')
        ensure_dir(directory)
        return directory

    def get_python_install_dir(self):
        return join(self.python_installs_dir, self.bootstrap.distribution.name)

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
    def ndk_api(self):
        '''The API number compile against'''
        if self._ndk_api is None:
            raise ValueError('Tried to access ndk_api but it has not '
                             'been set - this should not happen, something '
                             'went wrong!')
        return self._ndk_api

    @ndk_api.setter
    def ndk_api(self, value):
        self._ndk_api = value

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

    def prepare_build_environment(self,
                                  user_sdk_dir,
                                  user_ndk_dir,
                                  user_android_api,
                                  user_ndk_api):
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
                             d.endswith(('.bz2', '.gz'))]
            if possible_dirs:
                info('Found possible SDK dirs in buildozer dir: {}'.format(
                    ', '.join(d.split(os.sep)[-1] for d in possible_dirs)))
                info('Will attempt to use SDK at {}'.format(possible_dirs[0]))
                warning('This SDK lookup is intended for debug only, if you '
                        'use python-for-android much you should probably '
                        'maintain your own SDK download.')
                sdk_dir = possible_dirs[0]
        if sdk_dir is None:
            raise BuildInterruptingException('Android SDK dir was not specified, exiting.')
        self.sdk_dir = realpath(sdk_dir)

        # Check what Android API we're using
        android_api = None
        if user_android_api:
            android_api = user_android_api
            info('Getting Android API version from user argument: {}'.format(android_api))
        elif 'ANDROIDAPI' in environ:
            android_api = environ['ANDROIDAPI']
            info('Found Android API target in $ANDROIDAPI: {}'.format(android_api))
        else:
            info('Android API target was not set manually, using '
                 'the default of {}'.format(RECOMMENDED_TARGET_API))
            android_api = RECOMMENDED_TARGET_API
        android_api = int(android_api)
        self.android_api = android_api

        check_target_api(android_api, self.archs[0].arch)
        apis = get_available_apis(self.sdk_dir)
        info('Available Android APIs are ({})'.format(
            ', '.join(map(str, apis))))
        if android_api in apis:
            info(('Requested API target {} is available, '
                  'continuing.').format(android_api))
        else:
            raise BuildInterruptingException(
                ('Requested API target {} is not available, install '
                 'it with the SDK android tool.').format(android_api))

        # Find the Android NDK
        # Could also use ANDROID_NDK, but doesn't look like many tools use this
        ndk_dir = None
        if user_ndk_dir:
            ndk_dir = user_ndk_dir
            info('Getting NDK dir from from user argument')
        if ndk_dir is None:  # The old P4A-specific dir
            ndk_dir = environ.get('ANDROIDNDK', None)
            if ndk_dir is not None:
                info('Found NDK dir in $ANDROIDNDK: {}'.format(ndk_dir))
        if ndk_dir is None:  # Apparently the most common convention
            ndk_dir = environ.get('NDK_HOME', None)
            if ndk_dir is not None:
                info('Found NDK dir in $NDK_HOME: {}'.format(ndk_dir))
        if ndk_dir is None:  # Another convention (with maven?)
            ndk_dir = environ.get('ANDROID_NDK_HOME', None)
            if ndk_dir is not None:
                info('Found NDK dir in $ANDROID_NDK_HOME: {}'.format(ndk_dir))
        if ndk_dir is None:  # Checks in the buildozer NDK dir, useful
            #                # for debug tests of p4a
            possible_dirs = glob.glob(expanduser(join(
                '~', '.buildozer', 'android', 'platform', 'android-ndk-r*')))
            if possible_dirs:
                info('Found possible NDK dirs in buildozer dir: {}'.format(
                    ', '.join(d.split(os.sep)[-1] for d in possible_dirs)))
                info('Will attempt to use NDK at {}'.format(possible_dirs[0]))
                warning('This NDK lookup is intended for debug only, if you '
                        'use python-for-android much you should probably '
                        'maintain your own NDK download.')
                ndk_dir = possible_dirs[0]
        if ndk_dir is None:
            raise BuildInterruptingException('Android NDK dir was not specified')
        self.ndk_dir = realpath(ndk_dir)

        check_ndk_version(ndk_dir)

        ndk_api = None
        if user_ndk_api:
            ndk_api = user_ndk_api
            info('Getting NDK API version (i.e. minimum supported API) from user argument')
        elif 'NDKAPI' in environ:
            ndk_api = environ.get('NDKAPI', None)
            info('Found Android API target in $NDKAPI')
        else:
            ndk_api = min(self.android_api, RECOMMENDED_NDK_API)
            warning('NDK API target was not set manually, using '
                    'the default of {} = min(android-api={}, default ndk-api={})'.format(
                        ndk_api, self.android_api, RECOMMENDED_NDK_API))
        ndk_api = int(ndk_api)
        self.ndk_api = ndk_api

        check_ndk_api(ndk_api, self.android_api)

        # path to some tools
        self.ccache = sh.which("ccache")
        if not self.ccache:
            info('ccache is missing, the build will not be optimized in the '
                 'future.')
        try:
            subprocess.check_output([
                "python3", "-m", "cython", "--help",
            ])
        except subprocess.CalledProcessError:
            warning('Cython for python3 missing. If you are building for '
                    ' a python 3 target (which is the default)'
                    ' then THINGS WILL BREAK.')

        # This would need to be changed if supporting multiarch APKs
        arch = self.archs[0]
        toolchain_prefix = arch.toolchain_prefix
        self.ndk_platform, ndk_platform_dir_exists = get_ndk_platform_dir(
            self.ndk_dir, self.ndk_api, arch)
        ok = ok and ndk_platform_dir_exists

        py_platform = sys.platform
        if py_platform in ['linux2', 'linux3']:
            py_platform = 'linux'
        toolchain_versions, toolchain_path_exists = get_toolchain_versions(
            self.ndk_dir, arch)
        ok = ok and toolchain_path_exists
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
                warning(f"Missing executable: {executable} is not installed")

        if not ok:
            raise BuildInterruptingException(
                'python-for-android cannot continue due to the missing executables above')

    def __init__(self):
        self.include_dirs = []

        self._build_env_prepared = False

        self._sdk_dir = None
        self._ndk_dir = None
        self._android_api = None
        self._ndk_api = None
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
            Archx86_64(self),
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
            raise BuildInterruptingException('Asked to compile for no Archs, so failing.')
        info('Will compile for the following archs: {}'.format(
            ', '.join(arch.arch for arch in self.archs)))

    def prepare_bootstrap(self, bootstrap):
        if not bootstrap:
            raise TypeError("None is not allowed for bootstrap")
        bootstrap.ctx = self
        self.bootstrap = bootstrap
        self.bootstrap.prepare_build_dir()
        self.bootstrap_build_dir = self.bootstrap.build_dir

    def prepare_dist(self):
        self.bootstrap.prepare_dist_dir()

    def get_site_packages_dir(self, arch=None):
        '''Returns the location of site-packages in the python-install build
        dir.
        '''
        return self.get_python_install_dir()

    def get_libs_dir(self, arch):
        '''The libs dir for a given arch.'''
        ensure_dir(join(self.libs_dir, arch))
        return join(self.libs_dir, arch)

    def has_lib(self, arch, lib):
        return exists(join(self.get_libs_dir(arch), lib))

    def has_package(self, name, arch=None):
        # If this is a file path, it'll need special handling:
        if (name.find("/") >= 0 or name.find("\\") >= 0) and \
                name.find("://") < 0:  # (:// would indicate an url)
            if not os.path.exists(name):
                # Non-existing dir, cannot look this up.
                return False
            try:
                name = get_package_name(os.path.abspath(name))
            except ValueError:
                # Failed to look up any meaningful name.
                return False

        # Try to look up recipe by name:
        try:
            recipe = Recipe.get_recipe(name, self)
        except ValueError:
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


def build_recipes(build_order, python_modules, ctx, project_dir,
                  ignore_project_setup_py=False
                 ):
    # Put recipes in correct build order
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
            recipe.install_libraries(arch)

        # 4) biglink everything
        info_main('# Biglinking object files')
        if not ctx.python_recipe:
            biglink(ctx, arch)
        else:
            warning(
                "Context's python recipe found, "
                "skipping biglink (will this work?)"
            )

        # 5) postbuild packages
        info_main('# Postbuilding recipes')
        for recipe in recipes:
            info_main('Postbuilding {} for {}'.format(recipe.name, arch.arch))
            recipe.postbuild_arch(arch)

    info_main('# Installing pure Python modules')
    run_pymodules_install(
        ctx, python_modules, project_dir,
        ignore_setup_py=ignore_project_setup_py
    )


def project_has_setup_py(project_dir):
    return (project_dir is not None and
            (exists(join(project_dir, "setup.py")) or
             exists(join(project_dir, "pyproject.toml"))
            ))


def run_setuppy_install(ctx, project_dir, env=None):
    env = env or {}

    with current_directory(project_dir):
        info('got setup.py or similar, running project install. ' +
             '(disable this behavior with --ignore-setup-py)')

        # Compute & output the constraints we will use:
        info('Contents that will be used for constraints.txt:')
        constraints = subprocess.check_output([
            join(
                ctx.build_dir, "venv", "bin", "pip"
            ),
            "freeze"
        ], env=copy.copy(env))
        with suppress(AttributeError):
            constraints = constraints.decode("utf-8", "replace")
        info(constraints)

        # Make sure all packages found are fixed in version
        # by writing a constraint file, to avoid recipes being
        # upgraded & reinstalled:
        with open('._tmp_p4a_recipe_constraints.txt', 'wb') as fileh:
            fileh.write(constraints.encode("utf-8", "replace"))
        try:

            info('Populating venv\'s site-packages with '
                 'ctx.get_site_packages_dir()...')

            # Copy dist contents into site-packages for discovery.
            # Why this is needed:
            # --target is somewhat evil and messes with discovery of
            # packages in PYTHONPATH if that also includes the target
            # folder. So we need to use the regular virtualenv
            # site-packages folder instead.
            # Reference:
            # https://github.com/pypa/pip/issues/6223
            ctx_site_packages_dir = os.path.normpath(
                os.path.abspath(ctx.get_site_packages_dir())
            )
            venv_site_packages_dir = os.path.normpath(os.path.join(
                ctx.build_dir, "venv", "lib", [
                    f for f in os.listdir(os.path.join(
                        ctx.build_dir, "venv", "lib"
                    )) if f.startswith("python")
                ][0], "site-packages"
            ))
            copied_over_contents = []
            for f in os.listdir(ctx_site_packages_dir):
                full_path = os.path.join(ctx_site_packages_dir, f)
                if not os.path.exists(os.path.join(
                            venv_site_packages_dir, f
                        )):
                    if os.path.isdir(full_path):
                        shutil.copytree(full_path, os.path.join(
                            venv_site_packages_dir, f
                        ))
                    else:
                        shutil.copy2(full_path, os.path.join(
                            venv_site_packages_dir, f
                        ))
                    copied_over_contents.append(f)

            # Get listing of virtualenv's site-packages, to see the
            # newly added things afterwards & copy them back into
            # the distribution folder / build context site-packages:
            previous_venv_contents = os.listdir(
                venv_site_packages_dir
            )

            # Actually run setup.py:
            info('Launching package install...')
            shprint(sh.bash, '-c', (
                "'" + join(
                    ctx.build_dir, "venv", "bin", "pip"
                ).replace("'", "'\"'\"'") + "' " +
                "install -c ._tmp_p4a_recipe_constraints.txt -v ."
            ).format(ctx.get_site_packages_dir().
                     replace("'", "'\"'\"'")),
                    _env=copy.copy(env))

            # Go over all new additions and copy them back:
            info('Copying additions resulting from setup.py back '
                 'into ctx.get_site_packages_dir()...')
            new_venv_additions = []
            for f in (set(os.listdir(venv_site_packages_dir)) -
                      set(previous_venv_contents)):
                new_venv_additions.append(f)
                full_path = os.path.join(venv_site_packages_dir, f)
                if os.path.isdir(full_path):
                    shutil.copytree(full_path, os.path.join(
                        ctx_site_packages_dir, f
                    ))
                else:
                    shutil.copy2(full_path, os.path.join(
                        ctx_site_packages_dir, f
                    ))

            # Undo all the changes we did to the venv-site packages:
            info('Reverting additions to '
                 'virtualenv\'s site-packages...')
            for f in set(copied_over_contents + new_venv_additions):
                full_path = os.path.join(venv_site_packages_dir, f)
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
        finally:
            os.remove("._tmp_p4a_recipe_constraints.txt")


def run_pymodules_install(ctx, modules, project_dir=None,
                          ignore_setup_py=False):
    """ This function will take care of all non-recipe things, by:

        1. Processing them from --requirements (the modules argument)
           and installing them

        2. Installing the user project/app itself via setup.py if
           ignore_setup_py=True

    """

    info('*** PYTHON PACKAGE / PROJECT INSTALL STAGE ***')
    modules = list(filter(ctx.not_has_package, modules))

    # We change current working directory later, so this has to be an absolute
    # path or `None` in case that we didn't supply the `project_dir` via kwargs
    project_dir = abspath(project_dir) if project_dir else None

    # Bail out if no python deps and no setup.py to process:
    if not modules and (
            ignore_setup_py or
            project_dir is None or
            not project_has_setup_py(project_dir)
            ):
        info('No Python modules and no setup.py to process, skipping')
        return

    # Output messages about what we're going to do:
    if modules:
        info('The requirements ({}) don\'t have recipes, attempting to '
             'install them with pip'.format(', '.join(modules)))
        info('If this fails, it may mean that the module has compiled '
             'components and needs a recipe.')
    if project_dir is not None and \
            project_has_setup_py(project_dir) and not ignore_setup_py:
        info('Will process project install, if it fails then the '
             'project may not be compatible for Android install.')

    # Use our hostpython to create the virtualenv
    host_python = sh.Command(ctx.hostpython)
    with current_directory(join(ctx.build_dir)):
        shprint(host_python, '-m', 'venv', 'venv')

        # Prepare base environment and upgrade pip:
        base_env = dict(copy.copy(os.environ))
        base_env["PYTHONPATH"] = ctx.get_site_packages_dir()
        info('Upgrade pip to latest version')
        shprint(sh.bash, '-c', (
            "source venv/bin/activate && pip install -U pip"
        ), _env=copy.copy(base_env))

        # Install Cython in case modules need it to build:
        info('Install Cython in case one of the modules needs it to build')
        shprint(sh.bash, '-c', (
            "venv/bin/pip install Cython"
        ), _env=copy.copy(base_env))

        # Get environment variables for build (with CC/compiler set):
        standard_recipe = CythonRecipe()
        standard_recipe.ctx = ctx
        # (note: following line enables explicit -lpython... linker options)
        standard_recipe.call_hostpython_via_targetpython = False
        recipe_env = standard_recipe.get_recipe_env(ctx.archs[0])
        env = copy.copy(base_env)
        env.update(recipe_env)

        # Make sure our build package dir is available, and the virtualenv
        # site packages come FIRST (so the proper pip version is used):
        env["PYTHONPATH"] += ":" + ctx.get_site_packages_dir()
        env["PYTHONPATH"] = os.path.abspath(join(
            ctx.build_dir, "venv", "lib",
            "python" + ctx.python_recipe.major_minor_version_string,
            "site-packages")) + ":" + env["PYTHONPATH"]

        # Install the manually specified requirements first:
        if not modules:
            info('There are no Python modules to install, skipping')
        else:
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
            info('IF THIS FAILS, THE MODULES MAY NEED A RECIPE. '
                 'A reason for this is often modules compiling '
                 'native code that is unaware of Android cross-compilation '
                 'and does not work without additional '
                 'changes / workarounds.')

            shprint(sh.bash, '-c', (
                "venv/bin/pip " +
                "install -v --target '{0}' --no-deps -r requirements.txt"
            ).format(ctx.get_site_packages_dir().replace("'", "'\"'\"'")),
                    _env=copy.copy(env))

        # Afterwards, run setup.py if present:
        if project_dir is not None and (
                project_has_setup_py(project_dir) and not ignore_setup_py
                ):
            run_setuppy_install(ctx, project_dir, env)
        elif not ignore_setup_py:
            info("No setup.py found in project directory: " +
                 str(project_dir)
                )

        # Strip object files after potential Cython or native code builds:
        if not ctx.with_debug_symbols:
            standard_recipe.strip_object_files(
                ctx.archs[0], env, build_dir=ctx.build_dir
            )


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


def biglink_function(soname, objs_paths, extra_link_dirs=None, env=None):
    if extra_link_dirs is None:
        extra_link_dirs = []
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


def copylibs_function(soname, objs_paths, extra_link_dirs=None, env=None):
    if extra_link_dirs is None:
        extra_link_dirs = []
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
    shprint(sh.cp, *sofiles, dest)
