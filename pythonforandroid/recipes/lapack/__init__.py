'''
known to build with cmake version 3.19.2 and NDK r19c.
See https://gitlab.kitware.com/cmake/cmake/-/issues/18739
'''

from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory, ensure_dir, BuildInterruptingException
from multiprocessing import cpu_count
from os.path import join
import sh
from os import environ
from pythonforandroid.util import build_platform

arch_to_sysroot = {'armeabi': 'arm', 'armeabi-v7a': 'arm', 'arm64-v8a': 'arm64'}


class LapackRecipe(Recipe):

    name = 'lapack'
    version = 'v3.9.0'
    url = 'https://github.com/Reference-LAPACK/lapack/archive/{version}.tar.gz'
    libdir = 'build/install/lib'
    built_libraries = {'libblas.so': libdir, 'liblapack.so': libdir, 'libcblas.so': libdir}

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        ndk_dir = environ.get("LEGACY_NDK")
        if ndk_dir is None:
            raise BuildInterruptingException("Please set the environment variable 'LEGACY_NDK' to point to a NDK location with gcc/gfortran support (last tested NDK version was 'r19c')")

        GCC_VER = '4.9'
        HOST = build_platform

        sysroot_suffix = arch_to_sysroot.get(arch.arch, arch.arch)
        sysroot = f"{ndk_dir}/platforms/{env['NDK_API']}/arch-{sysroot_suffix}"
        FC = f"{ndk_dir}/toolchains/{arch.command_prefix}-{GCC_VER}/prebuilt/{HOST}/bin/{arch.command_prefix}-gfortran"
        env['FC'] = f'{FC} --sysroot={sysroot}'
        if sh.which(FC) is None:
            raise BuildInterruptingException(f"{FC} not found. See https://github.com/mzakharo/android-gfortran")
        return env

    def build_arch(self, arch):
        source_dir = self.get_build_dir(arch.arch)
        build_target = join(source_dir, 'build')
        install_target = join(build_target, 'install')

        ensure_dir(build_target)
        with current_directory(build_target):
            env = self.get_recipe_env(arch)
            ndk_dir = environ["LEGACY_NDK"]
            shprint(sh.rm, '-rf', 'CMakeFiles/', 'CMakeCache.txt', _env=env)
            shprint(sh.cmake, source_dir,
                    '-DCMAKE_SYSTEM_NAME=Android',
                    '-DCMAKE_POSITION_INDEPENDENT_CODE=1',
                    '-DCMAKE_ANDROID_ARCH_ABI={arch}'.format(arch=arch.arch),
                    '-DCMAKE_ANDROID_NDK=' + ndk_dir,
                    '-DCMAKE_BUILD_TYPE=Release',
                    '-DCMAKE_INSTALL_PREFIX={}'.format(install_target),
                    '-DANDROID_ABI={arch}'.format(arch=arch.arch),
                    '-DANDROID_ARM_NEON=ON',
                    '-DENABLE_NEON=ON',
                    '-DCBLAS=ON',
                    '-DBUILD_SHARED_LIBS=ON',
                    _env=env)
            shprint(sh.make, '-j' + str(cpu_count()), _env=env)
            shprint(sh.make, 'install', _env=env)


recipe = LapackRecipe()
