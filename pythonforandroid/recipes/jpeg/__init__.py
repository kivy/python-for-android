from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
from os.path import join
import sh


class JpegRecipe(Recipe):
    '''
    .. versionchanged:: 0.6.0
        rewrote recipe to be build with clang and updated libraries to latest
        version of the official git repo.
    '''
    name = 'jpeg'
    version = '2.0.1'
    url = 'https://github.com/libjpeg-turbo/libjpeg-turbo/archive/{version}.tar.gz'  # noqa
    built_libraries = {'libjpeg.a': '.', 'libturbojpeg.a': '.'}
    # we will require this below patch to build the shared library
    # patches = ['remove-version.patch']

    def build_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)

        # TODO: Fix simd/neon
        with current_directory(build_dir):
            env = self.get_recipe_env(arch)
            toolchain_file = join(self.ctx.ndk_dir,
                                  'build/cmake/android.toolchain.cmake')

            shprint(sh.rm, '-f', 'CMakeCache.txt', 'CMakeFiles/')
            shprint(sh.cmake, '-G', 'Unix Makefiles',
                    '-DCMAKE_SYSTEM_NAME=Android',
                    '-DCMAKE_POSITION_INDEPENDENT_CODE=1',
                    '-DCMAKE_ANDROID_ARCH_ABI={arch}'.format(arch=arch.arch),
                    '-DCMAKE_ANDROID_NDK=' + self.ctx.ndk_dir,
                    '-DCMAKE_C_COMPILER={cc}'.format(cc=arch.get_clang_exe()),
                    '-DCMAKE_CXX_COMPILER={cc_plus}'.format(
                        cc_plus=arch.get_clang_exe(plus_plus=True)),
                    '-DCMAKE_BUILD_TYPE=Release',
                    '-DCMAKE_INSTALL_PREFIX=./install',
                    '-DCMAKE_TOOLCHAIN_FILE=' + toolchain_file,

                    '-DANDROID_ABI={arch}'.format(arch=arch.arch),
                    '-DANDROID_ARM_NEON=ON',
                    '-DENABLE_NEON=ON',
                    # '-DREQUIRE_SIMD=1',

                    # Force disable shared, with the static ones is enough
                    '-DENABLE_SHARED=0',
                    '-DENABLE_STATIC=1',
                    _env=env)
            shprint(sh.make, _env=env)


recipe = JpegRecipe()
