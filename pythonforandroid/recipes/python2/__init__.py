
from pythonforandroid.toolchain import Recipe, shprint, get_directory, current_directory, ArchAndroid, info
from os.path import exists, join, realpath
from os import uname
import glob
import sh


class Python2Recipe(Recipe):
    version = "2.7.2"
    url = 'http://python.org/ftp/python/{version}/Python-{version}.tar.bz2'
    name = 'python2'

    depends = ['hostpython2']  
    conflicts = ['python3']

    def prebuild_armeabi(self):
        build_dir = self.get_build_container_dir('armeabi')
        if exists(join(build_dir, '.patched')):
            info('Python2 already patched, skipping.')
            return
        self.apply_patch(join('patches', 'Python-{}-xcompile.patch'.format(self.version)))
        self.apply_patch(join('patches', 'Python-{}-ctypes-disable-wchar.patch'.format(self.version)))
        self.apply_patch(join('patches', 'disable-modules.patch'))
        self.apply_patch(join('patches', 'fix-locale.patch'))
        self.apply_patch(join('patches', 'fix-gethostbyaddr.patch'))
        self.apply_patch(join('patches', 'fix-setup-flags.patch'))
        self.apply_patch(join('patches', 'fix-filesystemdefaultencoding.patch'))
        self.apply_patch(join('patches', 'fix-termios.patch'))
        self.apply_patch(join('patches', 'custom-loader.patch'))
        self.apply_patch(join('patches', 'verbose-compilation.patch'))
        self.apply_patch(join('patches', 'fix-remove-corefoundation.patch'))
        self.apply_patch(join('patches', 'fix-dynamic-lookup.patch'))
        self.apply_patch(join('patches', 'fix-dlfcn.patch'))
        # self.apply_patch(join('patches', 'ctypes-find-library.patch'))
        self.apply_patch(join('patches', 'ctypes-find-library-updated.patch'))

        if uname()[0] == 'Linux':
            self.apply_patch(join('patches', 'fix-configure-darwin.patch'))
            self.apply_patch(join('patches', 'fix-distutils-darwin.patch'))

        shprint(sh.touch, join(build_dir, '.patched'))

    def build_armeabi(self):

        if not exists(join(self.get_build_dir('armeabi'), 'libpython2.7.so')):
            self.do_python_build()

        if not exists(self.ctx.get_python_install_dir()):
            shprint(sh.cp, '-a', join(self.get_build_dir('armeabi'), 'python-install'),
                    self.ctx.get_python_install_dir())

        # This should be safe to run every time
        info('Copying hostpython binary to targetpython folder')
        shprint(sh.cp, self.ctx.hostpython,
                join(self.ctx.get_python_install_dir(), 'bin', 'python.host'))
        self.ctx.hostpython = join(self.ctx.get_python_install_dir(), 'bin', 'python.host')

        if not exists(join(self.ctx.get_libs_dir('armeabi'), 'libpython2.7.so')):
            shprint(sh.cp, join(self.get_build_dir('armeabi'), 'libpython2.7.so'), self.ctx.get_libs_dir('armeabi'))


        # # if exists(join(self.get_build_dir('armeabi'), 'libpython2.7.so')):
        # if exists(join(self.ctx.libs_dir, 'libpython2.7.so')):
        #     info('libpython2.7.so already exists, skipping python build.')
        #     if not exists(join(self.ctx.get_python_install_dir(), 'libpython2.7.so')):
        #         info('Copying python-install to dist-dependent location')
        #         shprint(sh.cp, '-a', 'python-install', self.ctx.get_python_install_dir())
        #     self.ctx.hostpython = join(self.ctx.get_python_install_dir(), 'bin', 'python.host')

        #     return

    def do_python_build(self):
        if 'sqlite' in self.ctx.recipe_build_order or 'openssl' in self.ctx.recipe_build_order:
            print('sqlite or openssl support not yet enabled in python recipe')
            exit(1)

        hostpython_recipe = Recipe.get_recipe('hostpython2', self.ctx)
        shprint(sh.cp, self.ctx.hostpython, self.get_build_dir('armeabi'))
        shprint(sh.cp, self.ctx.hostpgen, self.get_build_dir('armeabi'))
        hostpython = join(self.get_build_dir('armeabi'), 'hostpython')
        hostpgen = join(self.get_build_dir('armeabi'), 'hostpython')

        with current_directory(self.get_build_dir('armeabi')):


            hostpython_recipe = Recipe.get_recipe('hostpython2', self.ctx)
            shprint(sh.cp, join(hostpython_recipe.get_recipe_dir(), 'Setup'), 'Modules')

            env = ArchAndroid(self.ctx).get_env()

            # AND: Should probably move these to get_recipe_env for
            # neatness, but the whole recipe needs tidying along these
            # lines
            env['HOSTARCH'] = 'arm-eabi'
            env['BUILDARCH'] = shprint(sh.gcc, '-dumpmachine').stdout.split('\n')[0]
            env['CFLAGS'] = ' '.join([env['CFLAGS'], '-DNO_MALLINFO'])

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

            if uname()[0] == 'Darwin':
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
