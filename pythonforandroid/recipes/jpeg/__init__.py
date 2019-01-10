from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
from os.path import join, exists
from os import environ, uname
from glob import glob
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
    # we will require this below patch to build the shared library
    # patches = ['remove-version.patch']

    def should_build(self, arch):
        return not exists(join(self.get_build_dir(arch.arch),
                               'libturbojpeg.a'))

    def build_arch(self, arch):
        super(JpegRecipe, self).build_arch(arch)
        build_dir = self.get_build_dir(arch.arch)

        # TODO: Fix simd/neon
        with current_directory(build_dir):
            env = self.get_recipe_env(arch)
            toolchain_file = join(self.ctx.ndk_dir,
                                  'build/cmake/android.toolchain.cmake')

            shprint(sh.rm, '-f', 'CMakeCache.txt', 'CMakeFiles/')
            shprint(sh.cmake, '-G', 'Unix Makefiles',
                    '-DCMAKE_SYSTEM_NAME=Android',
                    '-DCMAKE_SYSTEM_PROCESSOR={cpu}'.format(cpu='arm'),
                    '-DCMAKE_POSITION_INDEPENDENT_CODE=1',
                    '-DCMAKE_ANDROID_ARCH_ABI={arch}'.format(arch=arch.arch),
                    '-DCMAKE_ANDROID_NDK=' + self.ctx.ndk_dir,
                    '-DCMAKE_C_COMPILER={toolchain}/bin/clang'.format(
                        toolchain=env['TOOLCHAIN']),
                    '-DCMAKE_CXX_COMPILER={toolchain}/bin/clang++'.format(
                        toolchain=env['TOOLCHAIN']),
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

            # copy static libs to libs collection
            for lib in glob(join(build_dir, '*.a')):
                shprint(sh.cp, '-L', lib, self.ctx.libs_dir)

    def get_recipe_env(self, arch=None, with_flags_in_cc=False, clang=True):
        env = environ.copy()

        build_platform = '{system}-{machine}'.format(
            system=uname()[0], machine=uname()[-1]).lower()
        env['TOOLCHAIN'] = join(self.ctx.ndk_dir, 'toolchains/llvm/'
                                'prebuilt/{build_platform}'.format(
                                    build_platform=build_platform))

        return env


recipe = JpegRecipe()
