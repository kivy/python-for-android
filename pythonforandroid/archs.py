from os.path import (join)
from os import environ, uname
import sys
from distutils.spawn import find_executable
from recipebases import Recipe

from pythonforandroid.logger import warning


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

    def get_env(self):
        env = {}

        env["CFLAGS"] = " ".join([
            "-DANDROID", "-mandroid", "-fomit-frame-pointer",
            "--sysroot", self.ctx.ndk_platform])

        env["CXXFLAGS"] = env["CFLAGS"]

        env["LDFLAGS"] = " ".join(['-lm'])

        py_platform = sys.platform
        if py_platform in ['linux2', 'linux3']:
            py_platform = 'linux'

        toolchain_prefix = self.ctx.toolchain_prefix
        toolchain_version = self.ctx.toolchain_version

        env['TOOLCHAIN_PREFIX'] = toolchain_prefix
        env['TOOLCHAIN_VERSION'] = toolchain_version

        if toolchain_prefix == 'x86':
            toolchain_prefix = 'i686-linux-android'
        print('path is', environ['PATH'])
        cc = find_executable('{toolchain_prefix}-gcc'.format(
            toolchain_prefix=toolchain_prefix), path=environ['PATH'])
        if cc is None:
            warning('Couldn\'t find executable for CC. This indicates a '
                    'problem locating the {} executable in the Android '
                    'NDK, not that you don\'t have a normal compiler '
                    'installed. Exiting.')
            exit(1)

        env['CC'] = '{toolchain_prefix}-gcc {cflags}'.format(
            toolchain_prefix=toolchain_prefix,
            cflags=env['CFLAGS'])
        env['CXX'] = '{toolchain_prefix}-g++ {cxxflags}'.format(
            toolchain_prefix=toolchain_prefix,
            cxxflags=env['CXXFLAGS'])

        env['AR'] = '{}-ar'.format(toolchain_prefix)
        env['RANLIB'] = '{}-ranlib'.format(toolchain_prefix)
        env['LD'] = '{}-ld'.format(toolchain_prefix)
        env['STRIP'] = '{}-strip --strip-unneeded'.format(toolchain_prefix)
        env['MAKE'] = 'make -j5'
        env['READELF'] = '{}-readelf'.format(toolchain_prefix)

        hostpython_recipe = Recipe.get_recipe('hostpython2', self.ctx)

        # AND: This hardcodes python version 2.7, needs fixing
        env['BUILDLIB_PATH'] = join(
            hostpython_recipe.get_build_dir(self.arch),
            'build', 'lib.linux-{}-2.7'.format(uname()[-1]))

        env['PATH'] = environ['PATH']

        env['ARCH'] = self.arch

        return env


class ArchARM(Arch):
    arch = "armeabi"
    toolchain_prefix = 'arm-linux-androideabi'
    command_prefix = 'arm-linux-androideabi'
    platform_dir = 'arch-arm'


class ArchARMv7_a(ArchARM):
    arch = 'armeabi-v7a'

    def get_env(self):
        env = super(ArchARMv7_a, self).get_env()
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

    def get_env(self):
        env = super(Archx86, self).get_env()
        env['CFLAGS'] = (env['CFLAGS'] +
                         ' -march=i686 -mtune=intel -mssse3 -mfpmath=sse -m32')
        env['CXXFLAGS'] = env['CFLAGS']
        return env


class Archx86_64(Arch):
    arch = 'x86_64'
    toolchain_prefix = 'x86'
    command_prefix = 'x86_64-linux-android'
    platform_dir = 'arch-x86'

    def get_env(self):
        env = super(Archx86_64, self).get_env()
        env['CFLAGS'] = (env['CFLAGS'] +
                         ' -march=x86-64 -msse4.2 -mpopcnt -m64 -mtune=intel')
        env['CXXFLAGS'] = env['CFLAGS']
        return env
