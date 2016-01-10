
from pythonforandroid.toolchain import Recipe, shprint, current_directory, ArchARM
from os.path import exists, join
from os import uname
import glob
import sh

class Python3Recipe(Recipe):
    version = '3.4.2'
    url = 'http://python.org/ftp/python/{version}/Python-{version}.tgz'
    name = 'python3'

    depends = ['hostpython3']  
    conflicts = ['python2']

    def __init__(self, **kwargs):
        super(Python3Recipe, self).__init__(**kwargs)

    def prebuild_arch(self, arch):
        build_dir = self.get_build_container_dir(arch.arch)
        if exists(join(build_dir, '.patched')):
            print('Python3 already patched, skipping.')
            return

        # # self.apply_patch(join('patches_inclement',
        # #                       'python-{version}-define_macro.patch'.format(version=self.version)))
        # # self.apply_patch(join('patches_inclement',
        # #                       'python-{version}-android-locale.patch'.format(version=self.version)))
        # # self.apply_patch(join('patches_inclement',
        # #                       'python-{version}-android-misc.patch'.format(version=self.version)))

        # self.apply_patch(join('patches_inclement',
        #                       'python-{version}-locale_and_android_misc.patch'.format(version=self.version)))
        

        self.apply_patch(join('patches', 'python-{version}-android-libmpdec.patch'.format(version=self.version)),
                         arch.arch)
        self.apply_patch(join('patches', 'python-{version}-android-locale.patch'.format(version=self.version)), arch.arch)
        self.apply_patch(join('patches', 'python-{version}-android-misc.patch'.format(version=self.version)), arch.arch)
        # self.apply_patch(join('patches', 'python-{version}-android-missing-getdents64-definition.patch'.format(version=self.version)), arch.arch)
        self.apply_patch(join('patches', 'python-{version}-cross-compile.patch'.format(version=self.version)), arch.arch)
        self.apply_patch(join('patches', 'python-{version}-python-misc.patch'.format(version=self.version)), arch.arch)

        self.apply_patch(join('patches', 'python-{version}-libpymodules_loader.patch'.format(version=self.version)), arch.arch)
        self.apply_patch('log_failures.patch', arch.arch)
        

        shprint(sh.touch, join(build_dir, '.patched'))

    def build_arch(self, arch):
        if 'sqlite' in self.ctx.recipe_build_order or 'openssl' in self.ctx.recipe_build_order:
            print('sqlite or openssl support not yet enabled in python recipe')
            exit(1)

        hostpython_recipe = Recipe.get_recipe('hostpython3', self.ctx)
        shprint(sh.cp, self.ctx.hostpython, self.get_build_dir(arch.arch))
        shprint(sh.cp, self.ctx.hostpgen, self.get_build_dir(arch.arch))
        hostpython = join(self.get_build_dir(arch.arch), 'hostpython')
        hostpgen = join(self.get_build_dir(arch.arch), 'hostpython')

        if exists(join(self.get_build_dir(arch.arch), 'libpython3.4m.so')):
            print('libpython3.4m.so already exists, skipping python build.')
            self.ctx.hostpython = join(self.ctx.build_dir, 'python-install',
                                       'bin', 'python.host')

            return

        with current_directory(self.get_build_dir(arch.arch)):


            hostpython_recipe = Recipe.get_recipe('hostpython3', self.ctx)
            # shprint(sh.cp, join(hostpython_recipe.get_recipe_dir(), 'Setup'), 'Modules')

            env = ArchARM(self.ctx).get_env()
            env["LDFLAGS"] = env["LDFLAGS"] + ' -llog'

            # AND: Should probably move these to get_recipe_env for
            # neatness, but the whole recipe needs tidying along these
            # lines
            env['HOSTARCH'] = 'arm-eabi'
            env['BUILDARCH'] = shprint(sh.gcc, '-dumpmachine').stdout
            # env['CFLAGS'] = ' '.join([env['CFLAGS'], '-DNO_MALLINFO'])

            env['HOSTARCH'] = 'arm-linux-androideabi'
            env['BUILDARCH'] = 'x86_64-pc-linux-gnu'

            configure = sh.Command('./configure')

            # AND: OFLAG isn't actually set, should it be?
            # shprint(configure,
            #         '--host={}'.format(env['HOSTARCH']),
            #         '--build={}'.format(env['BUILDARCH']),
            #         # 'OPT={}'.format(env['OFLAG']),
            #         '--prefix={}'.format(join(self.ctx.build_dir, 'python-install')),
            #         '--enable-shared',
            #         '--disable-toolbox-glue',
            #         '--disable-framefork',
            #         _env=env)

            with open('config.site', 'w') as fileh:
                fileh.write('''
    ac_cv_file__dev_ptmx=no
    ac_cv_file__dev_ptc=no
                ''')

            shprint(configure,
                    'CROSS_COMPILE_TARGET=yes',
                    'HOSTPYTHON={}'.format(hostpython),
                    'CONFIG_SITE=config.site',
                    '--prefix={}'.format(join(self.ctx.build_dir, 'python-install')),
                    '--host={}'.format(env['HOSTARCH']),
                    '--build={}'.format(env['BUILDARCH']),
                    '--disable-ipv6',
                    '--enable-shared',
                    '--without-ensurepip',
                    _env=env)

            # The python2 build always fails the first time, but python3 seems to work.

            make = sh.Command(env['MAKE'].split(' ')[0])
            # print('First install (expected to fail...')
            # try:
            #     shprint(make, '-j5', 'install', 'HOSTPYTHON={}'.format(hostpython),
            #             'HOSTPGEN={}'.format(hostpgen),
            #             'CROSS_COMPILE_TARGET=yes',
            #             'INSTSONAME=libpython3.7.so',
            #             _env=env)
            # except sh.ErrorReturnCode_2:
            #     print('First python3 make failed. This is expected, trying again.')
                

            # print('Second install (expected to work)')
            shprint(sh.touch, 'python.exe', 'python')
            # shprint(make, '-j5', 'install', 'HOSTPYTHON={}'.format(hostpython),
            #         'HOSTPGEN={}'.format(hostpgen),
            #         'CROSS_COMPILE_TARGET=yes',
            #         'INSTSONAME=libpython3.7.so',
            #         _env=env)

            shprint(make, '-j5',
                    'CROSS_COMPILE_TARGET=yes',
                    'HOSTPYTHON={}'.format(hostpython),
                    'HOSTPGEN={}'.format(hostpgen),
                    _env=env)

            shprint(make, '-j5', 'install',
                    'CROSS_COMPILE_TARGET=yes',
                    'HOSTPYTHON={}'.format(hostpython),
                    'HOSTPGEN={}'.format(hostpgen),
                    _env=env)

            # if uname()[0] == 'Darwin':
            #     shprint(sh.cp, join(self.get_recipe_dir(), 'patches', '_scproxy.py'),
            #             join(self.get_build_dir(), 'Lib'))
            #     shprint(sh.cp, join(self.get_recipe_dir(), 'patches', '_scproxy.py'),
            #             join(self.ctx.build_dir, 'python-install', 'lib', 'python3.7'))

            print('Ready to copy .so for python arm')
            shprint(sh.cp, 'libpython3.4m.so', self.ctx.libs_dir)
            shprint(sh.cp, 'libpython3.so', self.ctx.libs_dir)

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
                                           'lib', 'python3.7', dir_name))

        # print('python3 build done, exiting for debug')
        # exit(1)


recipe = Python3Recipe()
