
from pythonforandroid.recipe import TargetPythonRecipe, Recipe
from pythonforandroid.toolchain import shprint, current_directory, info
from pythonforandroid.patching import (is_linux, is_darwin, is_api_gt,
                                       check_all, is_api_lt, is_ndk)
from os.path import exists, join, realpath
import sh


class Python2Recipe(TargetPythonRecipe):
    version = "2.7.2"
    url = 'http://python.org/ftp/python/{version}/Python-{version}.tar.bz2'
    name = 'python2'

    depends = ['hostpython2']
    conflicts = ['python3crystax', 'python3']
    opt_depends = ['openssl','sqlite3']
    
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


        # # if exists(join(self.get_build_dir(arch.arch), 'libpython2.7.so')):
        # if exists(join(self.ctx.libs_dir, 'libpython2.7.so')):
        #     info('libpython2.7.so already exists, skipping python build.')
        #     if not exists(join(self.ctx.get_python_install_dir(), 'libpython2.7.so')):
        #         info('Copying python-install to dist-dependent location')
        #         shprint(sh.cp, '-a', 'python-install', self.ctx.get_python_install_dir())
        #     self.ctx.hostpython = join(self.ctx.get_python_install_dir(), 'bin', 'python.host')

        #     return

    def do_python_build(self, arch):

        hostpython_recipe = Recipe.get_recipe('hostpython2', self.ctx)
        shprint(sh.cp, self.ctx.hostpython, self.get_build_dir(arch.arch))
        shprint(sh.cp, self.ctx.hostpgen, self.get_build_dir(arch.arch))
        hostpython = join(self.get_build_dir(arch.arch), 'hostpython')
        hostpgen = join(self.get_build_dir(arch.arch), 'hostpython')

        with current_directory(self.get_build_dir(arch.arch)):


            hostpython_recipe = Recipe.get_recipe('hostpython2', self.ctx)
            shprint(sh.cp, join(hostpython_recipe.get_recipe_dir(), 'Setup'), 'Modules')

            env = arch.get_env()

            # AND: Should probably move these to get_recipe_env for
            # neatness, but the whole recipe needs tidying along these
            # lines
            env['HOSTARCH'] = 'arm-eabi'
            env['BUILDARCH'] = shprint(sh.gcc, '-dumpmachine').stdout.decode('utf-8').split('\n')[0]
            env['CFLAGS'] = ' '.join([env['CFLAGS'], '-DNO_MALLINFO'])

            # TODO need to add a should_build that checks if optional
            # dependencies have changed (possibly in a generic way)
            if 'openssl' in self.ctx.recipe_build_order:
                r = Recipe.get_recipe('openssl', self.ctx)
                openssl_build_dir = r.get_build_dir(arch.arch)
                setuplocal = join('Modules', 'Setup.local')
                shprint(sh.cp, join(self.get_recipe_dir(), 'Setup.local-ssl'), setuplocal)
                shprint(sh.sed, '-i.backup', 's#^SSL=.*#SSL={}#'.format(openssl_build_dir), setuplocal)
                env['OPENSSL_VERSION'] = r.version

            if 'sqlite3' in self.ctx.recipe_build_order:
                # Include sqlite3 in python2 build
                r = Recipe.get_recipe('sqlite3', self.ctx)
                i = ' -I' + r.get_build_dir(arch.arch)
                l = ' -L' + r.get_lib_dir(arch) + ' -lsqlite3'
                # Insert or append to env
                f = 'CPPFLAGS'
                env[f] = env[f] + i if f in env else i
                f = 'LDFLAGS'
                env[f] = env[f] + l if f in env else l

            # NDK has langinfo.h but doesn't define nl_langinfo()
            env['ac_cv_header_langinfo_h'] = 'no'
            configure = sh.Command('./configure')
            # AND: OFLAG isn't actually set, should it be?
            shprint(configure,
                    '--host={}'.format(env['HOSTARCH']),
                    '--build={}'.format(env['BUILDARCH']),
                    # 'OPT={}'.format(env['OFLAG']),
                    '--prefix={}'.format(realpath('./python-install')),
                    '--enable-shared',
                    '--disable-toolbox-glue',
                    '--disable-framework',
                    _env=env)

            # AND: tito left this comment in the original source. It's still true!
            # FIXME, the first time, we got a error at:
            # python$EXE ../../Tools/scripts/h2py.py -i '(u_long)' /usr/include/netinet/in.h
        # /home/tito/code/python-for-android/build/python/Python-2.7.2/python: 1: Syntax error: word unexpected (expecting ")")
            # because at this time, python is arm, not x86. even that, why /usr/include/netinet/in.h is used ?
            # check if we can avoid this part.

            make = sh.Command(env['MAKE'].split(' ')[0])
            print('First install (expected to fail...')
            try:
                shprint(make, '-j5', 'install', 'HOSTPYTHON={}'.format(hostpython),
                        'HOSTPGEN={}'.format(hostpgen),
                        'CROSS_COMPILE_TARGET=yes',
                        'INSTSONAME=libpython2.7.so',
                        _env=env)
            except sh.ErrorReturnCode_2:
                print('First python2 make failed. This is expected, trying again.')


            print('Second install (expected to work)')
            shprint(sh.touch, 'python.exe', 'python')
            shprint(make, '-j5', 'install', 'HOSTPYTHON={}'.format(hostpython),
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


            # info('Copying python-install to dist-dependent location')
            # shprint(sh.cp, '-a', 'python-install', self.ctx.get_python_install_dir())

            # print('Copying hostpython binary to targetpython folder')
            # shprint(sh.cp, self.ctx.hostpython,
            #         join(self.ctx.get_python_install_dir(), 'bin', 'python.host'))
            # self.ctx.hostpython = join(self.ctx.get_python_install_dir(), 'bin', 'python.host')



        # print('python2 build done, exiting for debug')
        # exit(1)


recipe = Python2Recipe()
