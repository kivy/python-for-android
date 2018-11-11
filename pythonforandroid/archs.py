from os.path import (exists, join, dirname)
from os import environ, uname
import sys
from distutils.spawn import find_executable

from pythonforandroid.logger import warning
from pythonforandroid.recipe import Recipe


class Arch(object):

    toolchain_prefix = None
    '''The prefix for the toolchain dir in the NDK.'''

    command_prefix = None
    '''The prefix for NDK commands such as gcc.'''

    def __init__(self, ctx):
        super(Arch, self).__init__()
        self.ctx = ctx

    def __str__(self):
        return self.arch

    @property
    def include_dirs(self):
        return [
            "{}/{}".format(
                self.ctx.include_dir,
                d.format(arch=self))
            for d in self.ctx.include_dirs]

    def get_env(self, with_flags_in_cc=True):
        env = {}

        env['CFLAGS'] = ' '.join([
            '-DANDROID', '-mandroid', '-fomit-frame-pointer'
            ' -D__ANDROID_API__={}'.format(self.ctx.ndk_api),
            ])
        env['LDFLAGS'] = ' '

        sysroot = join(self.ctx._ndk_dir, 'sysroot')
        if exists(sysroot):
            # post-15 NDK per
            # https://android.googlesource.com/platform/ndk/+/ndk-r15-release/docs/UnifiedHeaders.md
            env['CFLAGS'] += ' -isystem {}/sysroot/usr/include/{}'.format(
                self.ctx.ndk_dir, self.ctx.toolchain_prefix)
        else:
            sysroot = self.ctx.ndk_platform
            env['CFLAGS'] += ' -I{}'.format(self.ctx.ndk_platform)
        env['CFLAGS'] += ' -isysroot {} '.format(sysroot)
        env['CFLAGS'] += '-I' + join(self.ctx.get_python_install_dir(),
                                     'include/python{}'.format(
                                         self.ctx.python_recipe.version[0:3])
                                    )

        env['LDFLAGS'] += '--sysroot {} '.format(self.ctx.ndk_platform)

        env["CXXFLAGS"] = env["CFLAGS"]

        env["LDFLAGS"] += " ".join(['-lm', '-L' + self.ctx.get_libs_dir(self.arch)])

        if self.ctx.ndk == 'crystax':
            env['LDFLAGS'] += ' -L{}/sources/crystax/libs/{} -lcrystax'.format(self.ctx.ndk_dir, self.arch)

        py_platform = sys.platform
        if py_platform in ['linux2', 'linux3']:
            py_platform = 'linux'

        toolchain_prefix = self.ctx.toolchain_prefix
        toolchain_version = self.ctx.toolchain_version
        command_prefix = self.command_prefix

        env['TOOLCHAIN_PREFIX'] = toolchain_prefix
        env['TOOLCHAIN_VERSION'] = toolchain_version

        ccache = ''
        if self.ctx.ccache and bool(int(environ.get('USE_CCACHE', '1'))):
            # print('ccache found, will optimize builds')
            ccache = self.ctx.ccache + ' '
            env['USE_CCACHE'] = '1'
            env['NDK_CCACHE'] = self.ctx.ccache
            env.update({k: v for k, v in environ.items() if k.startswith('CCACHE_')})

        cc = find_executable('{command_prefix}-gcc'.format(
            command_prefix=command_prefix), path=environ['PATH'])
        if cc is None:
            print('Searching path are: {!r}'.format(environ['PATH']))
            warning('Couldn\'t find executable for CC. This indicates a '
                    'problem locating the {} executable in the Android '
                    'NDK, not that you don\'t have a normal compiler '
                    'installed. Exiting.')
            exit(1)

        if with_flags_in_cc:
            env['CC'] = '{ccache}{command_prefix}-gcc {cflags}'.format(
                command_prefix=command_prefix,
                ccache=ccache,
                cflags=env['CFLAGS'])
            env['CXX'] = '{ccache}{command_prefix}-g++ {cxxflags}'.format(
                command_prefix=command_prefix,
                ccache=ccache,
                cxxflags=env['CXXFLAGS'])
        else:
            env['CC'] = '{ccache}{command_prefix}-gcc'.format(
                command_prefix=command_prefix,
                ccache=ccache)
            env['CXX'] = '{ccache}{command_prefix}-g++'.format(
                command_prefix=command_prefix,
                ccache=ccache)

        env['AR'] = '{}-ar'.format(command_prefix)
        env['RANLIB'] = '{}-ranlib'.format(command_prefix)
        env['LD'] = '{}-ld'.format(command_prefix)
        env['LDSHARED'] = env["CC"] + " -pthread -shared " +\
            "-Wl,-O1 -Wl,-Bsymbolic-functions "
        if self.ctx.python_recipe and self.ctx.python_recipe.from_crystax:
            # For crystax python, we can't use the host python headers:
            env["CFLAGS"] += ' -I{}/sources/python/{}/include/python/'.\
                format(self.ctx.ndk_dir, self.ctx.python_recipe.version[0:3])
        env['STRIP'] = '{}-strip --strip-unneeded'.format(command_prefix)
        env['MAKE'] = 'make -j5'
        env['READELF'] = '{}-readelf'.format(command_prefix)
        env['NM'] = '{}-nm'.format(command_prefix)

        hostpython_recipe = Recipe.get_recipe('hostpython2', self.ctx)

        # This hardcodes python version 2.7, needs fixing
        env['BUILDLIB_PATH'] = join(
            hostpython_recipe.get_build_dir(self.arch),
            'build', 'lib.linux-{}-2.7'.format(uname()[-1]))

        env['PATH'] = environ['PATH']

        env['ARCH'] = self.arch
        env['NDK_API'] = 'android-{}'.format(str(self.ctx.ndk_api))

        if self.ctx.python_recipe and self.ctx.python_recipe.from_crystax:
            env['CRYSTAX_PYTHON_VERSION'] = self.ctx.python_recipe.version

        return env


class ArchARM(Arch):
    arch = "armeabi"
    toolchain_prefix = 'arm-linux-androideabi'
    command_prefix = 'arm-linux-androideabi'
    platform_dir = 'arch-arm'


class ArchARMv7_a(ArchARM):
    arch = 'armeabi-v7a'

    def get_env(self, with_flags_in_cc=True):
        env = super(ArchARMv7_a, self).get_env(with_flags_in_cc)
        env['CFLAGS'] = (env['CFLAGS'] +
                         (' -march=armv7-a -mfloat-abi=softfp '
                          '-mfpu=vfp -mthumb'))
        env['CXXFLAGS'] = env['CFLAGS']
        return env


class Archx86(Arch):
    arch = 'x86'
    toolchain_prefix = 'x86'
    command_prefix = 'i686-linux-android'
    platform_dir = 'arch-x86'

    def get_env(self, with_flags_in_cc=True):
        env = super(Archx86, self).get_env(with_flags_in_cc)
        env['CFLAGS'] = (env['CFLAGS'] +
                         ' -march=i686 -mtune=intel -mssse3 -mfpmath=sse -m32')
        env['CXXFLAGS'] = env['CFLAGS']
        return env


class Archx86_64(Arch):
    arch = 'x86_64'
    toolchain_prefix = 'x86'
    command_prefix = 'x86_64-linux-android'
    platform_dir = 'arch-x86'

    def get_env(self, with_flags_in_cc=True):
        env = super(Archx86_64, self).get_env(with_flags_in_cc)
        env['CFLAGS'] = (env['CFLAGS'] +
                         ' -march=x86-64 -msse4.2 -mpopcnt -m64 -mtune=intel')
        env['CXXFLAGS'] = env['CFLAGS']
        return env


class ArchAarch_64(Arch):
    arch = 'arm64-v8a'
    toolchain_prefix = 'aarch64-linux-android'
    command_prefix = 'aarch64-linux-android'
    platform_dir = 'arch-arm64'

    def get_env(self, with_flags_in_cc=True):
        env = super(ArchAarch_64, self).get_env(with_flags_in_cc)
        incpath = ' -I' + join(dirname(__file__), 'includes', 'arm64-v8a')
        env['EXTRA_CFLAGS'] = incpath
        env['CFLAGS'] += incpath
        env['CXXFLAGS'] += incpath
        if with_flags_in_cc:
            env['CC'] += incpath
            env['CXX'] += incpath
        return env
