from pythonforandroid.recipe import TargetPythonRecipe, Recipe
from pythonforandroid.toolchain import shprint, current_directory
from pythonforandroid.patching import (is_darwin, is_api_gt,
                                       check_all, is_api_lt, is_ndk)
from pythonforandroid.logger import logger, info, debug
from pythonforandroid.util import ensure_dir
from os.path import exists, join, realpath, basename
from os import environ, listdir, walk
import glob
from fnmatch import fnmatch
import sh


STDLIB_DIR_BLACKLIST = {
    '__pycache__',
    'test',
    'tests',
    'lib2to3',
    'ensurepip',
    'idlelib',
    'tkinter',
    }

STDLIB_FILEN_BLACKLIST = [
    '*.pyc',
    '*.exe',
    '*.whl',
    ]



class Python3Recipe(TargetPythonRecipe):
    version = '3.7.1'
    url = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'
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

            if not exists('python'):
                shprint(sh.make, 'all', _env=env)

            # TODO: Look into passing the path to pyconfig.h in a
            # better way, although this is probably acceptable
            sh.cp('pyconfig.h', join(recipe_build_dir, 'Include'))

    def include_root(self, arch_name):
        return join(self.get_build_dir(arch_name),
                    'Include')

    def link_root(self, arch_name):
        return join(self.get_build_dir(arch_name),
                    'android-build')

    def create_python_bundle(self, dirn, arch):
        ndk_dir = self.ctx.ndk_dir

        # Bundle compiled python modules to a folder
        modules_dir = join(dirn, 'modules')
        ensure_dir(modules_dir)

        modules_build_dir = join(
            self.get_build_dir(arch.arch),
            'android-build',
            'build',
            'lib.linux-arm-3.7')
        module_filens = (glob.glob(join(modules_build_dir, '*.so')) +
                         glob.glob(join(modules_build_dir, '*.py')))
        for filen in module_filens:
            shprint(sh.cp, filen, modules_dir)

        # zip up the standard library
        stdlib_zip = join(dirn, 'stdlib.zip')
        with current_directory(join(self.get_build_dir(arch.arch), 'Lib')):
            stdlib_filens = self.get_stdlib_filens('.')
            shprint(sh.zip, stdlib_zip, *stdlib_filens)

        # copy the site-packages into place
        shprint(sh.cp, '-r', self.ctx.get_python_install_dir(),
                join(dirn, 'site-packages'))

        # copy the python .so files into place
        python_build_dir = join(self.get_build_dir(arch.arch),
                                'android-build')
        shprint(sh.cp,
                join(python_build_dir,
                     'libpython{}m.so'.format(self.major_minor_version_string)),
                'libs/{}'.format(arch.arch))
        shprint(sh.cp,
                join(python_build_dir,
                     'libpython{}m.so.1.0'.format(self.major_minor_version_string)),
                'libs/{}'.format(arch.arch))

        info('Renaming .so files to reflect cross-compile')
        self.reduce_object_file_names(join(dirn, 'site-packages'))

    def get_stdlib_filens(self, basedir):
        return_filens = []
        for dirn, subdirs, filens in walk(basedir):
            if basename(dirn) in STDLIB_DIR_BLACKLIST:
                debug('stdlib.zip ignoring directory {}'.format(dirn))
                while subdirs:
                    subdirs.pop()
                continue
            for filen in filens:
                for pattern in STDLIB_FILEN_BLACKLIST:
                    if fnmatch(filen, pattern):
                        debug('stdlib.zip ignoring file {}'.format(join(dirn, filen)))
                        break
                else:
                    return_filens.append(join(dirn, filen))
        return return_filens
                    
                


recipe = Python3Recipe()
