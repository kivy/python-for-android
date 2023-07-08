import glob
import sh
import subprocess

from os import environ, utime
from os.path import dirname, exists, join
from pathlib import Path
import shutil

from pythonforandroid.logger import info, warning, shprint
from pythonforandroid.patching import version_starts_with
from pythonforandroid.recipe import Recipe, TargetPythonRecipe
from pythonforandroid.util import (
    current_directory,
    ensure_dir,
    walk_valid_filens,
    BuildInterruptingException,
)

NDK_API_LOWER_THAN_SUPPORTED_MESSAGE = (
    'Target ndk-api is {ndk_api}, '
    'but the python3 recipe supports only {min_ndk_api}+'
)


class Python3Recipe(TargetPythonRecipe):
    '''
    The python3's recipe
    ^^^^^^^^^^^^^^^^^^^^

    The python 3 recipe can be built with some extra python modules, but to do
    so, we need some libraries. By default, we ship the python3 recipe with
    some common libraries, defined in ``depends``. We also support some optional
    libraries, which are less common that the ones defined in ``depends``, so
    we added them as optional dependencies (``opt_depends``).

    Below you have a relationship between the python modules and the recipe
    libraries::

        - _ctypes: you must add the recipe for ``libffi``.
        - _sqlite3: you must add the recipe for ``sqlite3``.
        - _ssl: you must add the recipe for ``openssl``.
        - _bz2: you must add the recipe for ``libbz2`` (optional).
        - _lzma: you must add the recipe for ``liblzma`` (optional).

    .. note:: This recipe can be built only against API 21+.

    .. versionchanged:: 2019.10.06.post0
        - Refactored from deleted class ``python.GuestPythonRecipe`` into here
        - Added optional dependencies: :mod:`~pythonforandroid.recipes.libbz2`
          and :mod:`~pythonforandroid.recipes.liblzma`

    .. versionchanged:: 0.6.0
        Refactored into class
        :class:`~pythonforandroid.python.GuestPythonRecipe`
    '''

    version = '3.11.5'
    url = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'
    name = 'python3'

    patches = [
        'patches/pyconfig_detection.patch',
        'patches/reproducible-buildinfo.diff',

        # Python 3.7.1
        ('patches/py3.7.1_fix-ctypes-util-find-library.patch', version_starts_with("3.7")),
        ('patches/py3.7.1_fix-zlib-version.patch', version_starts_with("3.7")),

        # Python 3.8.1 & 3.9.X
        ('patches/py3.8.1.patch', version_starts_with("3.8")),
        ('patches/py3.8.1.patch', version_starts_with("3.9")),
        ('patches/py3.8.1.patch', version_starts_with("3.10")),
        ('patches/cpython-311-ctypes-find-library.patch', version_starts_with("3.11")),
    ]

    if shutil.which('lld') is not None:
        patches += [
            ("patches/py3.7.1_fix_cortex_a8.patch", version_starts_with("3.7")),
            ("patches/py3.8.1_fix_cortex_a8.patch", version_starts_with("3.8")),
            ("patches/py3.8.1_fix_cortex_a8.patch", version_starts_with("3.9")),
            ("patches/py3.8.1_fix_cortex_a8.patch", version_starts_with("3.10")),
            ("patches/py3.8.1_fix_cortex_a8.patch", version_starts_with("3.11")),
        ]

    depends = ['hostpython3', 'sqlite3', 'openssl', 'libffi']
    # those optional depends allow us to build python compression modules:
    #   - _bz2.so
    #   - _lzma.so
    opt_depends = ['libbz2', 'liblzma']
    '''The optional libraries which we would like to get our python linked'''

    configure_args = (
        '--host={android_host}',
        '--build={android_build}',
        '--enable-shared',
        '--enable-ipv6',
        'ac_cv_file__dev_ptmx=yes',
        'ac_cv_file__dev_ptc=no',
        '--without-ensurepip',
        'ac_cv_little_endian_double=yes',
        'ac_cv_header_sys_eventfd_h=no',
        '--prefix={prefix}',
        '--exec-prefix={exec_prefix}',
        '--enable-loadable-sqlite-extensions'
    )

    if version_starts_with("3.11"):
        configure_args += ('--with-build-python={python_host_bin}',)

    '''The configure arguments needed to build the python recipe. Those are
    used in method :meth:`build_arch` (if not overwritten like python3's
    recipe does).
    '''

    MIN_NDK_API = 21
    '''Sets the minimal ndk api number needed to use the recipe.

    .. warning:: This recipe can be built only against API 21+, so it means
        that any class which inherits from class:`GuestPythonRecipe` will have
        this limitation.
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

    compiled_extension = '.pyc'
    '''the default extension for compiled python files.

    .. note:: the default extension for compiled python files has been .pyo for
        python 2.x-3.4 but as of Python 3.5, the .pyo filename extension is no
        longer used and has been removed in favour of extension .pyc
    '''

    def __init__(self, *args, **kwargs):
        self._ctx = None
        super().__init__(*args, **kwargs)

    @property
    def _libpython(self):
        '''return the python's library name (with extension)'''
        return 'libpython{link_version}.so'.format(
            link_version=self.link_version
        )

    @property
    def link_version(self):
        '''return the python's library link version e.g. 3.7m, 3.8'''
        major, minor = self.major_minor_version_string.split('.')
        flags = ''
        if major == '3' and int(minor) < 8:
            flags += 'm'
        return '{major}.{minor}{flags}'.format(
            major=major,
            minor=minor,
            flags=flags
        )

    def include_root(self, arch_name):
        return join(self.get_build_dir(arch_name), 'Include')

    def link_root(self, arch_name):
        return join(self.get_build_dir(arch_name), 'android-build')

    def should_build(self, arch):
        return not Path(self.link_root(arch.arch), self._libpython).is_file()

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        self.ctx.python_recipe = self

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch)
        env['HOSTARCH'] = arch.command_prefix

        env['CC'] = arch.get_clang_exe(with_target=True)

        env['PATH'] = (
            '{hostpython_dir}:{old_path}').format(
                hostpython_dir=self.get_recipe(
                    'host' + self.name, self.ctx).get_path_to_python(),
                old_path=env['PATH'])

        env['CFLAGS'] = ' '.join(
            [
                '-fPIC',
                '-DANDROID'
            ]
        )

        env['LDFLAGS'] = env.get('LDFLAGS', '')
        if shutil.which('lld') is not None:
            # Note: The -L. is to fix a bug in python 3.7.
            # https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=234409
            env['LDFLAGS'] += ' -L. -fuse-ld=lld'
        else:
            warning('lld not found, linking without it. '
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
            self.configure_args += \
                ('--with-openssl=' + recipe.get_build_dir(arch.arch),)
            add_flags(recipe.include_flags(arch),
                      recipe.link_dirs_flags(arch), recipe.link_libs_flags())

        for library_name in {'libbz2', 'liblzma'}:
            if library_name in self.ctx.recipe_build_order:
                info(f'Activating flags for {library_name}')
                recipe = Recipe.get_recipe(library_name, self.ctx)
                add_flags(recipe.get_library_includes(arch),
                          recipe.get_library_ldflags(arch),
                          recipe.get_library_libs_flag())

        # python build system contains hardcoded zlib version which prevents
        # the build of zlib module, here we search for android's zlib version
        # and sets the right flags, so python can be build with android's zlib
        info("Activating flags for android's zlib")
        zlib_lib_path = arch.ndk_lib_dir_versioned
        zlib_includes = self.ctx.ndk.sysroot_include_dir
        zlib_h = join(zlib_includes, 'zlib.h')
        try:
            with open(zlib_h) as fileh:
                zlib_data = fileh.read()
        except IOError:
            raise BuildInterruptingException(
                "Could not determine android's zlib version, no zlib.h ({}) in"
                " the NDK dir includes".format(zlib_h)
            )
        for line in zlib_data.split('\n'):
            if line.startswith('#define ZLIB_VERSION '):
                break
        else:
            raise BuildInterruptingException(
                'Could not parse zlib.h...so we cannot find zlib version,'
                'required by python build,'
            )
        env['ZLIB_VERSION'] = line.replace('#define ZLIB_VERSION ', '')
        add_flags(' -I' + zlib_includes, ' -L' + zlib_lib_path, ' -lz')

        return env

    def build_arch(self, arch):
        if self.ctx.ndk_api < self.MIN_NDK_API:
            raise BuildInterruptingException(
                NDK_API_LOWER_THAN_SUPPORTED_MESSAGE.format(
                    ndk_api=self.ctx.ndk_api, min_ndk_api=self.MIN_NDK_API
                ),
            )

        recipe_build_dir = self.get_build_dir(arch.arch)

        # Create a subdirectory to actually perform the build
        build_dir = join(recipe_build_dir, 'android-build')
        ensure_dir(build_dir)

        # TODO: Get these dynamically, like bpo-30386 does
        sys_prefix = '/usr/local'
        sys_exec_prefix = '/usr/local'

        env = self.get_recipe_env(arch)
        env = self.set_libs_flags(env, arch)

        android_build = sh.Command(
            join(recipe_build_dir,
                 'config.guess'))().stdout.strip().decode('utf-8')

        with current_directory(build_dir):
            if not exists('config.status'):
                shprint(
                    sh.Command(join(recipe_build_dir, 'configure')),
                    *(' '.join(self.configure_args).format(
                                    android_host=env['HOSTARCH'],
                                    android_build=android_build,
                                    python_host_bin=join(self.get_recipe(
                                        'host' + self.name, self.ctx
                                    ).get_path_to_python(), "python3"),
                                    prefix=sys_prefix,
                                    exec_prefix=sys_exec_prefix)).split(' '),
                    _env=env)

            # Python build does not seem to play well with make -j option from Python 3.11 and onwards
            # Before losing some time, please check issue
            # https://github.com/python/cpython/issues/101295 , as the root cause looks similar
            shprint(
                sh.make,
                'all',
                'INSTSONAME={lib_name}'.format(lib_name=self._libpython),
                _env=env
            )

            # TODO: Look into passing the path to pyconfig.h in a
            # better way, although this is probably acceptable
            sh.cp('pyconfig.h', join(recipe_build_dir, 'Include'))

    def compile_python_files(self, dir):
        '''
        Compile the python files (recursively) for the python files inside
        a given folder.

        .. note:: python2 compiles the files into extension .pyo, but in
            python3, and as of Python 3.5, the .pyo filename extension is no
            longer used...uses .pyc (https://www.python.org/dev/peps/pep-0488)
        '''
        args = [self.ctx.hostpython]
        args += ['-OO', '-m', 'compileall', '-b', '-f', dir]
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

        # Compile to *.pyc the python modules
        self.compile_python_files(modules_build_dir)
        # Compile to *.pyc the standard python library
        self.compile_python_files(join(self.get_build_dir(arch.arch), 'Lib'))
        # Compile to *.pyc the other python packages (site-packages)
        self.compile_python_files(self.ctx.get_python_install_dir(arch.arch))

        # Bundle compiled python modules to a folder
        modules_dir = join(dirn, 'modules')
        c_ext = self.compiled_extension
        ensure_dir(modules_dir)
        module_filens = (glob.glob(join(modules_build_dir, '*.so')) +
                         glob.glob(join(modules_build_dir, '*' + c_ext)))
        info("Copy {} files into the bundle".format(len(module_filens)))
        for filen in module_filens:
            info(" - copy {}".format(filen))
            shutil.copy2(filen, modules_dir)

        # zip up the standard library
        stdlib_zip = join(dirn, 'stdlib.zip')
        with current_directory(join(self.get_build_dir(arch.arch), 'Lib')):
            stdlib_filens = list(walk_valid_filens(
                '.', self.stdlib_dir_blacklist, self.stdlib_filen_blacklist))
            if 'SOURCE_DATE_EPOCH' in environ:
                # for reproducible builds
                stdlib_filens.sort()
                timestamp = int(environ['SOURCE_DATE_EPOCH'])
                for filen in stdlib_filens:
                    utime(filen, (timestamp, timestamp))
            info("Zip {} files into the bundle".format(len(stdlib_filens)))
            shprint(sh.zip, '-X', stdlib_zip, *stdlib_filens)

        # copy the site-packages into place
        ensure_dir(join(dirn, 'site-packages'))
        ensure_dir(self.ctx.get_python_install_dir(arch.arch))
        # TODO: Improve the API around walking and copying the files
        with current_directory(self.ctx.get_python_install_dir(arch.arch)):
            filens = list(walk_valid_filens(
                '.', self.site_packages_dir_blacklist,
                self.site_packages_filen_blacklist))
            info("Copy {} files into the site-packages".format(len(filens)))
            for filen in filens:
                info(" - copy {}".format(filen))
                ensure_dir(join(dirn, 'site-packages', dirname(filen)))
                shutil.copy2(filen, join(dirn, 'site-packages', filen))

        # copy the python .so files into place
        python_build_dir = join(self.get_build_dir(arch.arch),
                                'android-build')
        python_lib_name = 'libpython' + self.link_version
        shprint(
            sh.cp,
            join(python_build_dir, python_lib_name + '.so'),
            join(self.ctx.bootstrap.dist_dir, 'libs', arch.arch)
        )

        info('Renaming .so files to reflect cross-compile')
        self.reduce_object_file_names(join(dirn, 'site-packages'))

        return join(dirn, 'site-packages')


recipe = Python3Recipe()
