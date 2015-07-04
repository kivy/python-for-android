
from pythonforandroid.toolchain import Recipe, shprint, get_directory, current_directory, ArchAndroid
from os.path import exists, join
from os import uname
import sh

class Python2Recipe(Recipe):
    version = "2.7.2"
    url = 'http://python.org/ftp/python/{version}/Python-{version}.tar.bz2'
    name = 'python2'

    depends = ['hostpython2']  

    def prebuild_armeabi(self):
        build_dir = self.get_build_container_dir('armeabi')
        if exists(join(build_dir, '.patched')):
            print('Python2 already patched, skipping.')
            return
        self.apply_patch(join('patches', 'Python-{}-xcompile.patch'.format(self.version)))
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

        if uname()[0] == 'Linux':
            self.apply_patch(join('patches', 'fix-configure-darwin.patch'))
            self.apply_patch(join('patches', 'fix-distutils-darwin.patch'))

        shprint(sh.touch, join(build_dir, '.patched'))

    def build_armeabi(self):
        if 'sqlite' in self.ctx.recipe_build_order or 'openssl' in self.ctx.recipe_build_order:
            print('sqlite or openssl support not yet enabled in python recipe')
            exit(1)

        hostpython_recipe = Recipe.get_recipe('hostpython2', self.ctx)
        shprint(sh.cp, self.ctx.hostpython, self.get_build_dir('armeabi'))
        shprint(sh.cp, self.ctx.hostpgen, self.get_build_dir('armeabi'))
        hostpython = join(self.get_build_dir('armeabi'), 'hostpython')
        hostpgen = join(self.get_build_dir('armeabi'), 'hostpython')

        if exists(join(self.get_build_dir('armeabi'), 'libpython2.7.so')):
            print('libpython2.7.so already exists, skipping python build.')
            self.ctx.hostpython = join(self.ctx.build_dir, 'python-install',
                                       'bin', 'python.host')

            return

        with current_directory(self.get_build_dir('armeabi')):


            hostpython_recipe = Recipe.get_recipe('hostpython2', self.ctx)
            shprint(sh.cp, join(hostpython_recipe.get_recipe_dir(), 'Setup'), 'Modules')

            env = ArchAndroid(self.ctx).get_env()

            configure = sh.Command('./configure')
            # AND: OFLAG isn't actually set, should it be?
            shprint(configure, '--host=arm-eabi',
                    # 'OPT={}'.format(env['OFLAG']),
                    '--prefix={}'.format(join(self.ctx.build_dir, 'python-install')),
                    '--enable-shared',
                    '--disable-toolbox-glue',
                    '--disable-framefork',
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
                        join(self.get_build_dir(), 'Lib'))
                shprint(sh.cp, join(self.get_recipe_dir(), 'patches', '_scproxy.py'),
                        join(self.ctx.build_dir, 'python-install', 'lib', 'python2.7'))

            print('Ready to copy .so for python arm')
            shprint(sh.cp, 'libpython2.7.so', self.ctx.libs_dir)

            print('Copying hostpython binary to targetpython folder')
            shprint(sh.cp, self.ctx.hostpython,
                    join(self.ctx.build_dir, 'python-install', 'bin',
                         'python.host'))
            self.ctx.hostpython = join(self.ctx.build_dir, 'python-install',
                                       'bin', 'python.host')


            # reduce python?
            for dir_name in ('test', join('json', 'tests'), 'lib-tk',
                             join('sqlite3', 'test'), join('unittest, test'),
                             join('lib2to3', 'tests'), join('bsddb', 'tests'),
                             join('distutils', 'tests'), join('email', 'test'),
                             'curses'):
                shprint(sh.rm, '-rf', join(self.ctx.build_dir, 'python-install',
                                           'lib', 'python2.7', dir_name))


recipe = Python2Recipe()
