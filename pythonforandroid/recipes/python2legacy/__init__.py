from pythonforandroid.recipe import TargetPythonRecipe, Recipe
from pythonforandroid.toolchain import shprint, current_directory, info
from pythonforandroid.patching import (is_darwin, is_api_gt,
                                       check_all, is_api_lt, is_ndk)
from multiprocessing import cpu_count
from os.path import exists, join, realpath
from os import walk
import glob
import sh

EXCLUDE_EXTS = (".py", ".pyc", ".so.o", ".so.a", ".so.libs", ".pyx")


class Python2LegacyRecipe(TargetPythonRecipe):
    '''
    .. warning:: This python2 recipe is the original one created by @tito and,
        for now, it is unusable.

    .. versionchanged:: 0.6.0
        This was the original python2's recipe moved to python2legacy.
    '''
    version = "2.7.2"
    url = 'https://python.org/ftp/python/{version}/Python-{version}.tar.bz2'
    name = 'python2legacy'

    depends = ['hostpython2legacy']
    conflicts = ['python3', 'python3crystax', 'python2']
    opt_depends = ['openssl', 'sqlite3']

    patches = ['patches/Python-{version}-xcompile.patch',
               'patches/Python-{version}-ctypes-disable-wchar.patch',
               'patches/disable-modules.patch',
               'patches/fix-locale.patch',
               'patches/fix-gethostbyaddr.patch',
               'patches/fix-setup-flags.patch',
               'patches/fix-filesystemdefaultencoding.patch',
               'patches/fix-termios.patch',
               'patches/custom-loader.patch',
               'patches/verbose-compilation.patch',
               'patches/fix-remove-corefoundation.patch',
               'patches/fix-dynamic-lookup.patch',
               'patches/fix-dlfcn.patch',
               'patches/parsetuple.patch',
               'patches/ctypes-find-library-updated.patch',
               ('patches/fix-configure-darwin.patch', is_darwin),
               ('patches/fix-distutils-darwin.patch', is_darwin),
               ('patches/fix-ftime-removal.patch', is_api_gt(19)),
               ('patches/disable-openpty.patch', check_all(is_api_lt(21), is_ndk('crystax')))]

    from_crystax = False

    def prebuild_arch(self, arch):
        super(Python2LegacyRecipe, self).prebuild_arch(arch)
        patch_mark = join(self.get_build_dir(arch.arch), '.openssl-patched')
        if 'openssl' in self.ctx.recipe_build_order and not exists(patch_mark):
            self.apply_patch(join('patches', 'enable-openssl.patch'), arch.arch)
            shprint(sh.touch, patch_mark)

    def build_arch(self, arch):

        if not exists(join(self.get_build_dir(arch.arch), 'libpython2.7.so')):
            self.do_python_build(arch)

        if not exists(self.ctx.get_python_install_dir()):
            shprint(sh.cp, '-a', join(self.get_build_dir(arch.arch), 'python-install'),
                    self.ctx.get_python_install_dir())

        # This should be safe to run every time
        info('Copying hostpython binary to targetpython folder')
        shprint(sh.cp, self.ctx.hostpython,
                join(self.ctx.get_python_install_dir(), 'bin', 'python.host'))
        self.ctx.hostpython = join(self.ctx.get_python_install_dir(), 'bin', 'python.host')

        if not exists(join(self.ctx.get_libs_dir(arch.arch), 'libpython2.7.so')):
            shprint(sh.cp, join(self.get_build_dir(arch.arch), 'libpython2.7.so'), self.ctx.get_libs_dir(arch.arch))

    def do_python_build(self, arch):

        shprint(sh.cp, self.ctx.hostpython, self.get_build_dir(arch.arch))
        shprint(sh.cp, self.ctx.hostpgen, self.get_build_dir(arch.arch))
        hostpython = join(self.get_build_dir(arch.arch), 'hostpython')
        hostpgen = join(self.get_build_dir(arch.arch), 'hostpython')

        with current_directory(self.get_build_dir(arch.arch)):

            hostpython_recipe = Recipe.get_recipe('hostpython2legacy', self.ctx)
            shprint(sh.cp, join(hostpython_recipe.get_recipe_dir(), 'Setup'), 'Modules')

            env = arch.get_env()

            env['HOSTARCH'] = 'arm-eabi'
            env['BUILDARCH'] = shprint(sh.gcc, '-dumpmachine').stdout.decode('utf-8').split('\n')[0]
            env['CFLAGS'] = ' '.join([env['CFLAGS'], '-DNO_MALLINFO'])

            # TODO need to add a should_build that checks if optional
            # dependencies have changed (possibly in a generic way)
            if 'openssl' in self.ctx.recipe_build_order:
                recipe = Recipe.get_recipe('openssl', self.ctx)
                openssl_build = recipe.get_build_dir(arch.arch)
                env['OPENSSL_BUILD'] = openssl_build
                env['OPENSSL_VERSION'] = recipe.version

            if 'sqlite3' in self.ctx.recipe_build_order:
                # Include sqlite3 in python2legacy build
                recipe = Recipe.get_recipe('sqlite3', self.ctx)
                include = ' -I' + recipe.get_build_dir(arch.arch)
                lib = ' -L' + recipe.get_lib_dir(arch) + ' -lsqlite3'
                # Insert or append to env
                flag = 'CPPFLAGS'
                env[flag] = env[flag] + include if flag in env else include
                flag = 'LDFLAGS'
                env[flag] = env[flag] + lib if flag in env else lib

            # NDK has langinfo.h but doesn't define nl_langinfo()
            env['ac_cv_header_langinfo_h'] = 'no'
            configure = sh.Command('./configure')
            shprint(configure,
                    '--host={}'.format(env['HOSTARCH']),
                    '--build={}'.format(env['BUILDARCH']),
                    # 'OPT={}'.format(env['OFLAG']),
                    '--prefix={}'.format(realpath('./python-install')),
                    '--enable-shared',
                    '--disable-toolbox-glue',
                    '--disable-framework',
                    _env=env)

            # tito left this comment in the original source. It's still true!
            # FIXME, the first time, we got a error at:
            # python$EXE ../../Tools/scripts/h2py.py -i '(u_long)' /usr/include/netinet/in.h  # noqa
            # /home/tito/code/python-for-android/build/python/Python-2.7.2/python: 1: Syntax error: word unexpected (expecting ")")  # noqa
            # because at this time, python is arm, not x86. even that,
            # why /usr/include/netinet/in.h is used ?
            # check if we can avoid this part.

            make = sh.Command(env['MAKE'].split(' ')[0])
            print('First install (expected to fail...')
            try:
                shprint(make, '-j' + str(cpu_count()), 'install',
                        'HOSTPYTHON={}'.format(hostpython),
                        'HOSTPGEN={}'.format(hostpgen),
                        'CROSS_COMPILE_TARGET=yes',
                        'INSTSONAME=libpython2.7.so',
                        _env=env)
            except sh.ErrorReturnCode_2:
                print('First python2 make failed. This is expected, trying again.')

            print('Second install (expected to work)')
            shprint(sh.touch, 'python.exe', 'python')
            shprint(make, '-j' + str(cpu_count()), 'install',
                    'HOSTPYTHON={}'.format(hostpython),
                    'HOSTPGEN={}'.format(hostpgen),
                    'CROSS_COMPILE_TARGET=yes',
                    'INSTSONAME=libpython2.7.so',
                    _env=env)

            if is_darwin():
                shprint(sh.cp, join(self.get_recipe_dir(), 'patches', '_scproxy.py'),
                        join('python-install', 'Lib'))
                shprint(sh.cp, join(self.get_recipe_dir(), 'patches', '_scproxy.py'),
                        join('python-install', 'lib', 'python2.7'))

            # reduce python
            for dir_name in ('test', join('json', 'tests'), 'lib-tk',
                             join('sqlite3', 'test'), join('unittest, test'),
                             join('lib2to3', 'tests'), join('bsddb', 'tests'),
                             join('distutils', 'tests'), join('email', 'test'),
                             'curses'):
                shprint(sh.rm, '-rf', join('python-install',
                                           'lib', 'python2.7', dir_name))

    def create_python_install(self, dist_dir):
        hostpython = sh.Command(self.ctx.hostpython)
        install_dir = self.ctx.get_python_install_dir()
        with current_directory(dist_dir):
            try:
                shprint(hostpython, '-OO', '-m', 'compileall',
                        install_dir,
                        _tail=10, _filterout="^Listing")
            except sh.ErrorReturnCode:
                pass
            if not exists('python-install'):
                shprint(sh.cp, '-a', install_dir, './python-install')

    def create_python_bundle(self, dirn, arch):
        info("Filling private directory")
        if not exists(join(dirn, "lib")):
            info("lib dir does not exist, making")
            shprint(sh.cp, "-a",
                    join("python-install", "lib"), dirn)
        shprint(sh.mkdir, "-p",
                join(dirn, "include", "python2.7"))

        libpymodules_fn = join("libs", arch.arch, "libpymodules.so")
        if exists(libpymodules_fn):
            shprint(sh.mv, libpymodules_fn, dirn)
        shprint(sh.cp,
                join('python-install', 'include',
                     'python2.7', 'pyconfig.h'),
                join(dirn, 'include', 'python2.7/'))

        info('Removing some unwanted files')
        shprint(sh.rm, '-f', join(dirn, 'lib', 'libpython2.7.so'))
        shprint(sh.rm, '-rf', join(dirn, 'lib', 'pkgconfig'))

        libdir = join(dirn, 'lib', 'python2.7')
        site_packages_dir = join(libdir, 'site-packages')
        with current_directory(libdir):
            removes = []
            for dirname, root, filenames in walk("."):
                for filename in filenames:
                    if filename.endswith(EXCLUDE_EXTS):
                        removes.append(filename)
            shprint(sh.rm, '-f', *removes)

            info('Deleting some other stuff not used on android')
            # To quote the original distribute.sh, 'well...'
            shprint(sh.rm, '-rf', 'lib2to3')
            shprint(sh.rm, '-rf', 'idlelib')
            shprint(sh.rm, '-f', *glob.glob('config/libpython*.a'))
            shprint(sh.rm, '-rf', 'config/python.o')

        return site_packages_dir

    def include_root(self, arch_name):
        return join(self.get_build_dir(arch_name), 'python-install', 'include', 'python2.7')

    def link_root(self, arch_name):
        return join(self.get_build_dir(arch_name), 'python-install', 'lib')


recipe = Python2LegacyRecipe()
