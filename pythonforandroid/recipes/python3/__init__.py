from pythonforandroid.recipe import TargetPythonRecipe, Recipe
from pythonforandroid.toolchain import shprint, current_directory, info
from pythonforandroid.patching import (is_darwin, is_api_gt,
                                       check_all, is_api_lt, is_ndk)
from pythonforandroid.logger import logger
from pythonforandroid.util import ensure_dir
from os.path import exists, join, realpath
from os import environ
import sh


class Python3Recipe(TargetPythonRecipe):
    version = 'bpo-30386'
    url = 'https://github.com/inclement/cpython/archive/{version}.zip'
    name = 'python3'

    depends = ['hostpython3']
    conflicts = ['python3crystax', 'python2']
    # opt_depends = ['openssl', 'sqlite3']

    def build_arch(self, arch):
        recipe_build_dir = self.get_build_dir(arch.arch)
        
        # Create a subdirectory to actually perform the build
        build_dir = join(recipe_build_dir, 'android-build')
        ensure_dir(build_dir)

        # TODO: Get these dynamically, like bpo-30386 does
        sys_prefix = '/usr/local'
        sys_exec_prefix = '/usr/local'

        # Skipping "Ensure that nl_langinfo is broken" from the original bpo-30386

        with current_directory(build_dir):
            env = environ.copy()

            # TODO: Get this information from p4a's arch system
            android_host = 'arm-linux-androideabi'
            android_build = sh.Command(join(recipe_build_dir, 'config.guess'))().stdout.strip().decode('utf-8')
            platform_dir = join(self.ctx.ndk_dir, 'platforms', 'android-21', 'arch-arm')
            toolchain = '{android_host}-4.9'.format(android_host=android_host)
            toolchain = join(self.ctx.ndk_dir, 'toolchains', toolchain, 'prebuilt', 'linux-x86_64')
            CC = '{clang} -target {target} -gcc-toolchain {toolchain}'.format(
                clang=join(self.ctx.ndk_dir, 'toolchains', 'llvm', 'prebuilt', 'linux-x86_64', 'bin', 'clang'),
                target='armv7-none-linux-androideabi',
                toolchain=toolchain)

            AR = join(toolchain, 'bin', android_host) + '-ar'
            LD = join(toolchain, 'bin', android_host) + '-ld'
            RANLIB = join(toolchain, 'bin', android_host) + '-ranlib'
            READELF = join(toolchain, 'bin', android_host) + '-readelf'
            STRIP = join(toolchain, 'bin', android_host) + '-strip --strip-debug --strip-unneeded'

            env['CC'] = CC
            env['AR'] = AR
            env['LD'] = LD
            env['RANLIB'] = RANLIB
            env['READELF'] = READELF
            env['STRIP'] = STRIP

            ndk_flags = '--sysroot={ndk_sysroot} -D__ANDROID_API__=21 -isystem {ndk_android_host}'.format(
                ndk_sysroot=join(self.ctx.ndk_dir, 'sysroot'),
                ndk_android_host=join(self.ctx.ndk_dir, 'sysroot', 'usr', 'include', android_host))
            sysroot = join(self.ctx.ndk_dir, 'platforms', 'android-21', 'arch-arm')
            env['CFLAGS'] = env.get('CFLAGS', '') + ' ' + ndk_flags
            env['CPPFLAGS'] = env.get('CPPFLAGS', '') + ' ' + ndk_flags
            env['LDFLAGS'] = env.get('LDFLAGS', '') + ' --sysroot={} -L{}'.format(sysroot, join(sysroot, 'usr', 'lib'))

            # Manually add the libs directory, and copy some object
            # files to the current directory otherwise they aren't
            # picked up. This seems necessary because the --sysroot
            # setting in LDFLAGS is overridden by the other flags.
            # TODO: Work out why this doesn't happen in the original
            # bpo-30386 Makefile system.
            logger.warning('Doing some hacky stuff to link properly')
            lib_dir = join(sysroot, 'usr', 'lib')
            env['LDFLAGS'] += ' -L{}'.format(lib_dir)
            shprint(sh.cp, join(lib_dir, 'crtbegin_so.o'), './')
            shprint(sh.cp, join(lib_dir, 'crtend_so.o'), './')

            env['SYSROOT'] = sysroot

            print('CPPflags', env['CPPFLAGS'])
            print('LDFLAGS', env['LDFLAGS'])

            print('LD is', env['LD'])

            if not exists('config.status'):
                shprint(sh.Command(join(recipe_build_dir, 'configure')),
                        *(' '.join(('--host={android_host}',
                                    '--build={android_build}',
                                    '--enable-shared',
                                    '--disable-ipv6',
                                    'ac_cv_file__dev_ptmx=yes',
                                    'ac_cv_file__dev_ptc=no',
                                    '--without-ensurepip',
                                    'ac_cv_little_endian_double=yes',
                                    '--prefix={prefix}',
                                    '--exec-prefix={exec_prefix}')).format(
                                        android_host=android_host,
                                        android_build=android_build,
                                        prefix=sys_prefix,
                                        exec_prefix=sys_exec_prefix)).split(' '), _env=env)

            import ipdb
            ipdb.set_trace()

            shprint(sh.make, 'all', _env=env)

            exit(1)
            

        #     if not exists('config.status'):
                

        #     shprint(sh.make, '-C', build_dir)
            

recipe = Python3Recipe()
