
from pythonforandroid.recipe import TargetPythonRecipe, Recipe
from pythonforandroid.toolchain import shprint, current_directory, info
from pythonforandroid.patching import (is_linux, is_darwin, is_api_gt,
                                       check_all, is_api_lt, is_ndk)
from os.path import exists, join, realpath
import sh
import shutil


class Python2Recipe(TargetPythonRecipe):
    version = "2.7.9"
    url = 'http://python.org/ftp/python/{version}/Python-{version}.tgz'
    name = 'python2'

    depends = ['hostpython2']
    conflicts = ['python3crystax', 'python3']
    opt_depends = ['openssl', 'libffi', 'sqlite3']

    patches = ['patches/Python-{version}-xcompile_mod.patch',
               'patches/Python_{version}-ctypes-libffi-fix-configure.patch',
               'patches/ffi-config.sub-{version}.patch',
               'patches/fix-locale-{version}.patch',
               'patches/modules-locales-{version}.patch',
               'patches/fix-platform-{version}.patch',
               'patches/fix-gethostbyaddr.patch',  # OLD 2.7.2 Patch
               'patches/basic-android-{version}_mod.patch',

               # APPLY OLD WORKING 2.7.2 PATCHES
               'patches/fix-filesystemdefaultencoding.patch',
               'patches/fix-termios.patch',
               'patches/custom-loader.patch',
               'patches/fix-remove-corefoundation.patch',
               'patches/fix-dynamic-lookup.patch',
               'patches/fix-dlfcn.patch',
               'patches/ctypes-find-library-updated.patch',

               # Todo: Regular Patches from 2.7.2, Not needed on 2.7.9, must be removed?
               # 'patches/Python-{version}-ctypes-disable-wchar.patch',
               # 'patches/disable-modules.patch',
               # 'patches/fix-setup-flags.patch',
               # 'patches/verbose-compilation.patch',

               # Todo: Untested Special Patches from 2.7.2, Will work on 2.7.9?
               # ('patches/fix-configure-darwin.patch', is_darwin),
               # ('patches/fix-distutils-darwin.patch', is_darwin),
               # ('patches/fix-ftime-removal.patch', is_api_gt(19)),
               # ('patches/disable-openpty.patch', check_all(is_api_lt(21), is_ndk('crystax')))
               ]

    from_crystax = False

    def prebuild_arch(self, arch):
        # Here we update some patches to our build system
        if not exists(join(self.get_build_dir(arch.arch), '.patched')):
            recipe_dir = self.get_recipe(self.name, arch.arch).recipe_dir

            # Creates a copy of xcompile.patch...to be adapted to our build
            patch_xcompile_base = join(recipe_dir, 'patches/Python-{0}-xcompile.patch'.format(self.version))
            patch_xcompile_mod = join(recipe_dir, 'patches/Python-{0}-xcompile_mod.patch'.format(self.version))
            shutil.copy(patch_xcompile_base, patch_xcompile_mod)

            # Creates a copy of basic-android.patch...to be adapted to our build
            patch_android_base = join(recipe_dir, 'patches/basic-android-{0}.patch'.format(self.version))
            patch_android_mod = join(recipe_dir, 'patches/basic-android-{0}_mod.patch'.format(self.version))
            shutil.copy(patch_android_base, patch_android_mod)

            # REWRITES PATCH TO MATCH SSL DIRS
            if 'openssl' in self.ctx.recipe_build_order:
                info("\t->Updating Python-{0}-xcompile.patch to support openssl".format(self.version))
                # REWRITING PATCH TO MATCH SSL LIBS DIR
                openssl_build_dir = Recipe.get_recipe('openssl', self.ctx).get_build_dir(arch.arch)
                shprint(sh.sed, '-i', 's#/path-to-ssl-build-dir#{}#'.format(openssl_build_dir), patch_xcompile_mod)

                info("\t->Updating  basic-android-{0}.patch to support openssl".format(self.version))
                shprint(sh.sed, '-i', 's#/path-to-ssl-build-dir#{}#'.format(openssl_build_dir), patch_android_mod)

            # REWRITES PATCH TO MATCH FFI DIRS
            if 'libffi' in self.ctx.recipe_build_order:
                info("\t->Updating  basic-android-{0}.patch to support libffi".format(self.version))
                ffi_inc_dir = join(Recipe.get_recipe('libffi', self.ctx).get_build_dir(arch.arch), 'include')
                ffi_libs_dir = self.ctx.get_libs_dir(arch.arch)
                shprint(sh.sed, '-i', 's#/path-to-ffi-include-dir#{}#'.format(ffi_inc_dir), patch_android_mod)
                shprint(sh.sed, '-i', 's#/path-to-ffi-lib-dir#{}#'.format(ffi_libs_dir), patch_android_mod)

            # REWRITES PATCH TO MATCH SQLITE3 DIRS
            use_sqlite3 = True
            if 'sqlite3' in self.ctx.recipe_build_order:
                sqlite_inc_dir = Recipe.get_recipe('sqlite3', self.ctx).get_jni_dir(arch)
                sqlite_libs_dir = Recipe.get_recipe('sqlite3', self.ctx).get_lib_dir(arch)
            elif 'pygame_bootstrap_components' in self.ctx.recipe_build_order:
                sqlite_inc_dir = join(Recipe.get_recipe('pygame_bootstrap_components', self.ctx).get_jni_dir(), 'sqlite3')
                sqlite_libs_dir = join(self.ctx.bootstrap_build_dir, 'obj', 'local', 'armeabi')
            else:
                use_sqlite3 = False
            if use_sqlite3:
                info("\t->Updating  basic-android-{0}.patch to support libsqlite3".format(self.version))
                shprint(sh.sed, '-i', 's#/path-to-sqlite3-include-dir#{}#'.format(sqlite_inc_dir), patch_android_mod)
                shprint(sh.sed, '-i', 's#/path-to-sqlite3-lib-dir#{}#'.format(sqlite_libs_dir), patch_android_mod)
        super(Python2Recipe, self).prebuild_arch(arch)

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
        shprint(sh.cp, self.ctx.hostpgen, join(self.get_build_dir(arch.arch), 'Parser'))
        hostpython = join(self.get_build_dir(arch.arch), 'hostpython')
        hostpgen = join(self.get_build_dir(arch.arch), 'Parser/hostpgen')

        with current_directory(self.get_build_dir(arch.arch)):
            hostpython_recipe = Recipe.get_recipe('hostpython2', self.ctx)
            shprint(sh.cp, join(hostpython_recipe.get_recipe_dir(), 'Setup'), 'Modules')
            # Hack to make it work from user recipes, referenced on python-for-android issues  #613
            # shprint(sh.cp, join(hostpython_recipe.recipe_dir, 'Setup'), 'Modules/Setup')

            env = arch.get_env()
            env.update({
                'RFS': "{0}/platforms/android-{1}/arch-arm".format(self.ctx.ndk_dir, self.ctx.android_api),
                })
            # info('\t-> RFS:               {}'.format(env['RFS']))
            # info('\t-> TOOLCHAIN_ROOT:    {}'.format(env['TOOLCHAIN_ROOT']))
            # info('\t-> android_api:    {}'.format(self.ctx.android_api))
            # info('\t-> ndk_dir:    {}'.format(self.ctx.ndk_dir))

            env.update({
                'HOSTARCH': 'arm-linux-androideabi',
                'BUILDARCH': shprint(sh.gcc, '-dumpmachine').stdout.split('\n')[0],
            })

            env['CFLAGS'] = ' '.join([env['CFLAGS'],
                                      '-g0', '-Os', '-s', '-I{0}/usr/include'.format(env['RFS']),
                                      '-fdata-sections', '-ffunction-sections',
                                      # '-DNO_MALLINFO'
                                      ])
            env['LDFLAGS'] = ' '.join([env['LDFLAGS'],
                                      '-L{0}/usr/lib'.format(env['RFS']), '-L{0}lib'.format(env['RFS'])])

            # TODO need to add a should_build that checks if optional
            # dependencies have changed (possibly in a generic way)
            if 'openssl' in self.ctx.recipe_build_order:
                openssl_build_dir = Recipe.get_recipe('openssl', self.ctx).get_build_dir(arch.arch)
                openssl_libs_dir = openssl_build_dir
                openssl_inc_dir = join(openssl_libs_dir, 'include')

                info("\t-> Openssl Inc dir => {0}".format(openssl_inc_dir))
                info("\t-> Openssl Libs dir => {0}".format(openssl_libs_dir))
                info("\t-> Openssl Build dir => {0}".format(openssl_build_dir))

                env['CFLAGS'] = ' '.join([env['CFLAGS'], '-I{}'.format(openssl_inc_dir),
                                          '-I{}/openssl'.format(openssl_inc_dir)])
                env['LDFLAGS'] = ' '.join([env['LDFLAGS'], '-L{}'.format(openssl_libs_dir), '-lcrypto', '-lssl'])

            if 'sqlite3' in self.ctx.recipe_build_order:
                info("Activate flags for sqlite3")
                sqlite_jni_dir = Recipe.get_recipe('sqlite3', self.ctx).get_jni_dir(arch)
                sqlite_libs_dir = Recipe.get_recipe('sqlite3', self.ctx).get_lib_dir(arch)
                # info("\t-> Sqlite3 Jni dir => {0}".format(sqlite_jni_dir))
                # info("\t-> Sqlite3 Libs dir => {0}".format(sqlite_libs_dir))

                env['CFLAGS'] = ' '.join([env['CFLAGS'], '-I{}'.format(sqlite_jni_dir)])
                env['LDFLAGS'] = ' '.join([env['LDFLAGS'], '-L{}'.format(sqlite_libs_dir), '-lsqlite3'])
            elif 'pygame_bootstrap_components' in self.ctx.recipe_build_order:
                info("Activate flags for sqlite3")
                sqlite_jni_dir = Recipe.get_recipe('pygame_bootstrap_components', self.ctx).get_jni_dir()
                sqlite_libs_dir = join(self.ctx.bootstrap_build_dir, 'obj', 'local', 'armeabi')
                # info("\t-> Sqlite3 Jni dir => {0}".format(sqlite_jni_dir))
                # info("\t-> Sqlite3 Libs dir => {0}".format(sqlite_libs_dir))

                env['CFLAGS'] = ' '.join([env['CFLAGS'], '-I{}/sqlite3'.format(sqlite_jni_dir)])
                env['LDFLAGS'] = ' '.join([env['LDFLAGS'], '-L{}'.format(sqlite_libs_dir), '-lsqlite3'])

            if 'libffi' in self.ctx.recipe_build_order:
                info("Activate flags for ffi")
                ffi_inc_dir = join(Recipe.get_recipe('libffi', self.ctx).get_build_dir(arch.arch), 'include')
                ffi_libs_dir = Recipe.get_recipe('libffi', self.ctx).get_lib_dir(arch)
                # info("\t-> Ffi Inc dir => {0}".format(ffi_inc_dir))
                # info("\t-> Ffi Libs dir => {0}".format(ffi_libs_dir))

                env['LIBFFI_CFLAGS'] = ' '.join([env['CFLAGS'], '-I{}'.format(ffi_inc_dir)])
                env['LIBFFI_LIBS'] = ' '.join(['-L{}'.format(ffi_libs_dir), '-lffi'])

                env['CFLAGS'] = ' '.join([env['CFLAGS'], '-I{}'.format(ffi_inc_dir)])
                env['LDFLAGS'] = ' '.join([env['LDFLAGS'], '-L{}'.format(ffi_libs_dir), '-lffi'])

            env['CFLAGS'] = ' '.join([env['CFLAGS'], '-Wformat'])

            configure = sh.Command('./configure')
            # AND: OFLAG isn't actually set, should it be?
            shprint(configure,
                    'CROSS_COMPILE_TARGET=yes',
                    '--host={}'.format(env['HOSTARCH']),
                    '--build={}'.format(env['BUILDARCH']),
                    # 'OPT={}'.format(env['OFLAG']),
                    '--prefix={}'.format(realpath('./python-install')),
                    '--enable-shared',
                    '--with-system-ffi',
                    '--disable-ipv6',
                    # '--disable-toolbox-glue',
                    # '--disable-framework',
                    'ac_cv_file__dev_ptmx=no',
                    'ac_cv_file__dev_ptc=no',
                    'ac_cv_have_long_long_format=yes',
                    'PYTHON_FOR_BUILD={}'.format(hostpython),
                    _env=env
                    )

            print('Make compile ...')
            shprint(sh.make, '-j5',
                    'CROSS_COMPILE_TARGET=yes',
                    'INSTSONAME=libpython2.7.so',
                    _env=env
                    )

            print('Make install ...')
            shprint(sh.make, '-j5', 'install',
                    'CROSS_COMPILE_TARGET=yes',
                    'INSTSONAME=libpython2.7.so',
                    _env=env
                    )

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
                shprint(sh.rm, '-rf', join(self.ctx.build_dir, 'python-install',
                                           'lib', 'python2.7', dir_name))


recipe = Python2Recipe()
