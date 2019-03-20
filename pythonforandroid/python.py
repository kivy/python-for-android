'''
This module is kind of special because it contains the base classes used to
build our python3 and python2 recipes and his corresponding hostpython recipes.
'''

from os.path import dirname, exists, join
from multiprocessing import cpu_count
from shutil import copy2
from os import environ
import subprocess
import glob
import sh

from pythonforandroid.recipe import Recipe, TargetPythonRecipe
from pythonforandroid.logger import logger, info, shprint
from pythonforandroid.util import (
    current_directory, ensure_dir, walk_valid_filens,
    BuildInterruptingException, build_platform)


class GuestPythonRecipe(TargetPythonRecipe):
    '''
    Class for target python recipes. Sets ctx.python_recipe to point to itself,
    so as to know later what kind of Python was built or used.

    This base class is used for our main python recipes (python2 and python3)
    which shares most of the build process.

    .. versionadded:: 0.6.0
        Refactored from the inclement's python3 recipe with a few changes:

        - Splits the python's build process several methods: :meth:`build_arch`
          and :meth:`get_recipe_env`.
        - Adds the attribute :attr:`configure_args`, which has been moved from
          the method :meth:`build_arch` into a static class variable.
        - Adds some static class variables used to create the python bundle and
          modifies the method :meth:`create_python_bundle`, to adapt to the new
          situation. The added static class variables are:
          :attr:`stdlib_dir_blacklist`, :attr:`stdlib_filen_blacklist`,
          :attr:`site_packages_dir_blacklist`and
          :attr:`site_packages_filen_blacklist`.
    '''

    MIN_NDK_API = 21
    '''Sets the minimal ndk api number needed to use the recipe.

    .. warning:: This recipe can be built only against API 21+, so it means
        that any class which inherits from class:`GuestPythonRecipe` will have
        this limitation.
    '''

    from_crystax = False
    '''True if the python is used from CrystaX, False otherwise (i.e. if
    it is built by p4a).'''

    configure_args = ()
    '''The configure arguments needed to build the python recipe. Those are
    used in method :meth:`build_arch` (if not overwritten like python3crystax's
    recipe does).

    .. note:: This variable should be properly set in subclass.
    '''

    stdlib_dir_blacklist = {
        '__pycache__',
        'test',
        'tests',
        'lib2to3',
        'ensurepip',
        'idlelib',
        'tkinter',
    }
    '''The directories that we want to omit for our python bundle'''

    stdlib_filen_blacklist = [
        '*.py',
        '*.exe',
        '*.whl',
    ]
    '''The file extensions that we want to blacklist for our python bundle'''

    site_packages_dir_blacklist = {
        '__pycache__',
        'tests'
    }
    '''The directories from site packages dir that we don't want to be included
    in our python bundle.'''

    site_packages_filen_blacklist = [
        '*.py'
    ]
    '''The file extensions from site packages dir that we don't want to be
    included in our python bundle.'''

    opt_depends = ['sqlite3', 'libffi', 'openssl']
    '''The optional libraries which we would like to get our python linked'''

    compiled_extension = '.pyc'
    '''the default extension for compiled python files.

    .. note:: the default extension for compiled python files has been .pyo for
        python 2.x-3.4 but as of Python 3.5, the .pyo filename extension is no
        longer used and has been removed in favour of extension .pyc
    '''

    def __init__(self, *args, **kwargs):
        self._ctx = None
        super(GuestPythonRecipe, self).__init__(*args, **kwargs)

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        if self.from_crystax:
            return super(GuestPythonRecipe, self).get_recipe_env(
                arch=arch, with_flags_in_cc=with_flags_in_cc)

        env = environ.copy()

        android_host = env['HOSTARCH'] = arch.command_prefix
        toolchain = '{toolchain_prefix}-{toolchain_version}'.format(
            toolchain_prefix=self.ctx.toolchain_prefix,
            toolchain_version=self.ctx.toolchain_version)
        toolchain = join(self.ctx.ndk_dir, 'toolchains',
                         toolchain, 'prebuilt', build_platform)

        env['CC'] = (
            '{clang} -target {target} -gcc-toolchain {toolchain}').format(
                clang=join(self.ctx.ndk_dir, 'toolchains', 'llvm', 'prebuilt',
                           build_platform, 'bin', 'clang'),
                target=arch.target,
                toolchain=toolchain)
        env['AR'] = join(toolchain, 'bin', android_host) + '-ar'
        env['LD'] = join(toolchain, 'bin', android_host) + '-ld'
        env['RANLIB'] = join(toolchain, 'bin', android_host) + '-ranlib'
        env['READELF'] = join(toolchain, 'bin', android_host) + '-readelf'
        env['STRIP'] = join(toolchain, 'bin', android_host) + '-strip'
        env['STRIP'] += ' --strip-debug --strip-unneeded'

        env['PATH'] = (
            '{hostpython_dir}:{old_path}').format(
                hostpython_dir=self.get_recipe(
                    'host' + self.name, self.ctx).get_path_to_python(),
                old_path=env['PATH'])

        ndk_flags = (
            '-fPIC --sysroot={ndk_sysroot} -D__ANDROID_API__={android_api} '
            '-isystem {ndk_android_host} -I{ndk_include}').format(
                ndk_sysroot=join(self.ctx.ndk_dir, 'sysroot'),
                android_api=self.ctx.ndk_api,
                ndk_android_host=join(
                    self.ctx.ndk_dir, 'sysroot', 'usr', 'include', android_host),
                ndk_include=join(self.ctx.ndk_dir, 'sysroot', 'usr', 'include'))
        sysroot = self.ctx.ndk_platform
        env['CFLAGS'] = env.get('CFLAGS', '') + ' ' + ndk_flags
        env['CPPFLAGS'] = env.get('CPPFLAGS', '') + ' ' + ndk_flags
        env['LDFLAGS'] = env.get('LDFLAGS', '') + ' --sysroot={} -L{}'.format(
            sysroot, join(sysroot, 'usr', 'lib'))

        # Manually add the libs directory, and copy some object
        # files to the current directory otherwise they aren't
        # picked up. This seems necessary because the --sysroot
        # setting in LDFLAGS is overridden by the other flags.
        # TODO: Work out why this doesn't happen in the original
        # bpo-30386 Makefile system.
        logger.warning('Doing some hacky stuff to link properly')
        lib_dir = join(sysroot, 'usr', 'lib')
        if arch.arch == 'x86_64':
            lib_dir = join(sysroot, 'usr', 'lib64')
        env['LDFLAGS'] += ' -L{}'.format(lib_dir)
        shprint(sh.cp, join(lib_dir, 'crtbegin_so.o'), './')
        shprint(sh.cp, join(lib_dir, 'crtend_so.o'), './')

        env['SYSROOT'] = sysroot

        if sh.which('lld') is not None:
            # Note: The -L. is to fix a bug in python 3.7.
            # https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=234409
            env["LDFLAGS"] += ' -L. -fuse-ld=lld'
        else:
            logger.warning('lld not found, linking without it. ' +
                           'Consider installing lld if linker errors occur.')

        return env

    def set_libs_flags(self, env, arch):
        '''Takes care to properly link libraries with python depending on our
        requirements and the attribute :attr:`opt_depends`.
        '''
        def add_flags(include_flags, link_dirs, link_libs):
            env['CPPFLAGS'] = env.get('CPPFLAGS', '') + include_flags
            env['LDFLAGS'] = env.get('LDFLAGS', '') + link_dirs
            env['LIBS'] = env.get('LIBS', '') + link_libs

        if 'sqlite3' in self.ctx.recipe_build_order:
            info('Activating flags for sqlite3')
            recipe = Recipe.get_recipe('sqlite3', self.ctx)
            add_flags(' -I' + recipe.get_build_dir(arch.arch),
                      ' -L' + recipe.get_lib_dir(arch), ' -lsqlite3')

        if 'libffi' in self.ctx.recipe_build_order:
            info('Activating flags for libffi')
            recipe = Recipe.get_recipe('libffi', self.ctx)
            # In order to force the correct linkage for our libffi library, we
            # set the following variable to point where is our libffi.pc file,
            # because the python build system uses pkg-config to configure it.
            env['PKG_CONFIG_PATH'] = recipe.get_build_dir(arch.arch)
            add_flags(' -I' + ' -I'.join(recipe.get_include_dirs(arch)),
                      ' -L' + join(recipe.get_build_dir(arch.arch), '.libs'),
                      ' -lffi')

        if 'openssl' in self.ctx.recipe_build_order:
            info('Activating flags for openssl')
            recipe = Recipe.get_recipe('openssl', self.ctx)
            add_flags(recipe.include_flags(arch),
                      recipe.link_dirs_flags(arch), recipe.link_libs_flags())
        return env

    def prebuild_arch(self, arch):
        super(TargetPythonRecipe, self).prebuild_arch(arch)
        if self.from_crystax and self.ctx.ndk != 'crystax':
            raise BuildInterruptingException(
                'The {} recipe can only be built when using the CrystaX NDK. '
                'Exiting.'.format(self.name))
        self.ctx.python_recipe = self

    def build_arch(self, arch):
        if self.ctx.ndk_api < self.MIN_NDK_API:
            raise BuildInterruptingException(
                'Target ndk-api is {}, but the python3 recipe supports only'
                ' {}+'.format(self.ctx.ndk_api, self.MIN_NDK_API))

        recipe_build_dir = self.get_build_dir(arch.arch)

        # Create a subdirectory to actually perform the build
        build_dir = join(recipe_build_dir, 'android-build')
        ensure_dir(build_dir)

        # TODO: Get these dynamically, like bpo-30386 does
        sys_prefix = '/usr/local'
        sys_exec_prefix = '/usr/local'

        with current_directory(build_dir):
            env = self.get_recipe_env(arch)
            env = self.set_libs_flags(env, arch)

            android_build = sh.Command(
                join(recipe_build_dir,
                     'config.guess'))().stdout.strip().decode('utf-8')

            if not exists('config.status'):
                shprint(
                    sh.Command(join(recipe_build_dir, 'configure')),
                    *(' '.join(self.configure_args).format(
                                    android_host=env['HOSTARCH'],
                                    android_build=android_build,
                                    prefix=sys_prefix,
                                    exec_prefix=sys_exec_prefix)).split(' '),
                    _env=env)

            if not exists('python'):
                py_version = self.major_minor_version_string
                if self.major_minor_version_string[0] == '3':
                    py_version += 'm'
                shprint(sh.make, 'all', '-j', str(cpu_count()),
                        'INSTSONAME=libpython{version}.so'.format(
                            version=py_version), _env=env)

            # TODO: Look into passing the path to pyconfig.h in a
            # better way, although this is probably acceptable
            sh.cp('pyconfig.h', join(recipe_build_dir, 'Include'))

    def include_root(self, arch_name):
        return join(self.get_build_dir(arch_name), 'Include')

    def link_root(self, arch_name):
        return join(self.get_build_dir(arch_name), 'android-build')

    def compile_python_files(self, dir):
        '''
        Compile the python files (recursively) for the python files inside
        a given folder.

        .. note:: python2 compiles the files into extension .pyo, but in
            python3, and as of Python 3.5, the .pyo filename extension is no
            longer used...uses .pyc (https://www.python.org/dev/peps/pep-0488)
        '''
        args = [self.ctx.hostpython]
        if self.ctx.python_recipe.name == 'python3':
            args += ['-OO', '-m', 'compileall', '-b', '-f', dir]
        else:
            args += ['-OO', '-m', 'compileall', '-f', dir]
        subprocess.call(args)

    def create_python_bundle(self, dirn, arch):
        """
        Create a packaged python bundle in the target directory, by
        copying all the modules and standard library to the right
        place.
        """
        # Todo: find a better way to find the build libs folder
        modules_build_dir = join(
            self.get_build_dir(arch.arch),
            'android-build',
            'build',
            'lib.linux{}-{}-{}'.format(
                '2' if self.version[0] == '2' else '',
                arch.command_prefix.split('-')[0],
                self.major_minor_version_string
            ))

        # Compile to *.pyc/*.pyo the python modules
        self.compile_python_files(modules_build_dir)
        # Compile to *.pyc/*.pyo the standard python library
        self.compile_python_files(join(self.get_build_dir(arch.arch), 'Lib'))
        # Compile to *.pyc/*.pyo the other python packages (site-packages)
        self.compile_python_files(self.ctx.get_python_install_dir())

        # Bundle compiled python modules to a folder
        modules_dir = join(dirn, 'modules')
        c_ext = self.compiled_extension
        ensure_dir(modules_dir)
        module_filens = (glob.glob(join(modules_build_dir, '*.so')) +
                         glob.glob(join(modules_build_dir, '*' + c_ext)))
        info("Copy {} files into the bundle".format(len(module_filens)))
        for filen in module_filens:
            info(" - copy {}".format(filen))
            copy2(filen, modules_dir)

        # zip up the standard library
        stdlib_zip = join(dirn, 'stdlib.zip')
        with current_directory(join(self.get_build_dir(arch.arch), 'Lib')):
            stdlib_filens = list(walk_valid_filens(
                '.', self.stdlib_dir_blacklist, self.stdlib_filen_blacklist))
            info("Zip {} files into the bundle".format(len(stdlib_filens)))
            shprint(sh.zip, stdlib_zip, *stdlib_filens)

        # copy the site-packages into place
        ensure_dir(join(dirn, 'site-packages'))
        ensure_dir(self.ctx.get_python_install_dir())
        # TODO: Improve the API around walking and copying the files
        with current_directory(self.ctx.get_python_install_dir()):
            filens = list(walk_valid_filens(
                '.', self.site_packages_dir_blacklist,
                self.site_packages_filen_blacklist))
            info("Copy {} files into the site-packages".format(len(filens)))
            for filen in filens:
                info(" - copy {}".format(filen))
                ensure_dir(join(dirn, 'site-packages', dirname(filen)))
                copy2(filen, join(dirn, 'site-packages', filen))

        # copy the python .so files into place
        python_build_dir = join(self.get_build_dir(arch.arch),
                                'android-build')
        python_lib_name = 'libpython' + self.major_minor_version_string
        if self.major_minor_version_string[0] == '3':
            python_lib_name += 'm'
        shprint(sh.cp, join(python_build_dir, python_lib_name + '.so'),
                join(self.ctx.dist_dir, self.ctx.dist_name, 'libs', arch.arch))

        info('Renaming .so files to reflect cross-compile')
        self.reduce_object_file_names(join(dirn, 'site-packages'))

        return join(dirn, 'site-packages')


class HostPythonRecipe(Recipe):
    '''
    This is the base class for hostpython3 and hostpython2 recipes. This class
    will take care to do all the work to build a hostpython recipe but, be
    careful, it is intended to be subclassed because some of the vars needs to
    be set:

        - :attr:`name`
        - :attr:`version`

    .. versionadded:: 0.6.0
        Refactored from the hostpython3's recipe by inclement
    '''

    name = ''
    '''The hostpython's recipe name. This should be ``hostpython2`` or
    ``hostpython3``

    .. warning:: This must be set in inherited class.'''

    version = ''
    '''The hostpython's recipe version.

    .. warning:: This must be set in inherited class.'''

    build_subdir = 'native-build'
    '''Specify the sub build directory for the hostpython recipe. Defaults
    to ``native-build``.'''

    url = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'
    '''The default url to download our host python recipe. This url will
    change depending on the python version set in attribute :attr:`version`.'''

    def get_build_container_dir(self, arch=None):
        choices = self.check_recipe_choices()
        dir_name = '-'.join([self.name] + choices)
        return join(self.ctx.build_dir, 'other_builds', dir_name, 'desktop')

    def get_build_dir(self, arch=None):
        '''
        .. note:: Unlike other recipes, the hostpython build dir doesn't
            depend on the target arch
        '''
        return join(self.get_build_container_dir(), self.name)

    def get_path_to_python(self):
        return join(self.get_build_dir(), self.build_subdir)

    def build_arch(self, arch):
        recipe_build_dir = self.get_build_dir(arch.arch)

        # Create a subdirectory to actually perform the build
        build_dir = join(recipe_build_dir, self.build_subdir)
        ensure_dir(build_dir)

        if not exists(join(build_dir, 'python')):
            with current_directory(recipe_build_dir):
                # Configure the build
                with current_directory(build_dir):
                    if not exists('config.status'):
                        shprint(
                            sh.Command(join(recipe_build_dir, 'configure')))

                # Create the Setup file. This copying from Setup.dist
                # seems to be the normal and expected procedure.
                shprint(sh.cp, join('Modules', 'Setup.dist'),
                        join(build_dir, 'Modules', 'Setup'))

                shprint(sh.make, '-j', str(cpu_count()), '-C', build_dir)
        else:
            info('Skipping {name} ({version}) build, as it has already '
                 'been completed'.format(name=self.name, version=self.version))

        self.ctx.hostpython = join(build_dir, 'python')
