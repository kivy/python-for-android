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


class LapackRecipe(Recipe):

    name = 'lapack'
    version = 'v3.9.0'
    url = 'https://github.com/Reference-LAPACK/lapack/archive/{version}.tar.gz'
    libdir = 'build/install/lib'
    built_libraries = {'libblas.so': libdir, 'liblapack.so': libdir, 'libcblas.so': libdir}
    need_stl_shared = True

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        sysroot = f"{self.ctx.ndk_dir}/platforms/{env['NDK_API']}/{arch.platform_dir}"
        FC = f"{env['TOOLCHAIN_PREFIX']}-gfortran"
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
            shprint(sh.rm, '-rf', 'CMakeFiles/', 'CMakeCache.txt', _env=env)
            shprint(sh.cmake, source_dir,
                    '-DCMAKE_SYSTEM_NAME=Android',
                    '-DCMAKE_POSITION_INDEPENDENT_CODE=1',
                    '-DCMAKE_ANDROID_ARCH_ABI={arch}'.format(arch=arch.arch),
                    '-DCMAKE_ANDROID_NDK=' + self.ctx.ndk_dir,
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
