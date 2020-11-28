from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
from multiprocessing import cpu_count
import os
import sh


class LibLeptonicaRecipe(Recipe):
    version = '1.80.0'
    url = 'https://github.com/DanBloomberg/leptonica/releases/download/{version}/leptonica-{version}.tar.gz'
    md5sum = 'd640d684234442a84c9e8902f0b3ff36'
    sha256sum = 'ec9c46c2aefbb960fb6a6b7f800fe39de48343437b6ce08e30a8d9688ed14ba4'

    depends = ['png', 'jpeg']
    built_libraries = {'libleptonica.so': os.path.join('install', 'lib')}

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        source_dir = self.get_build_dir(arch.arch)
        build_dir = os.path.join(source_dir, 'build')
        install_dir = os.path.join(source_dir, 'install')
        shprint(sh.mkdir, '-p', build_dir)

        with current_directory(build_dir):
            shprint(sh.cmake, source_dir,
                    '-DANDROID_ABI={}'.format(arch.arch),
                    '-DANDROID_NATIVE_API_LEVEL={}'.format(self.ctx.ndk_api),

                    '-DCMAKE_TOOLCHAIN_FILE={}'.format(
                        os.path.join(self.ctx.ndk_dir, 'build', 'cmake',
                                     'android.toolchain.cmake')),
                    '-DCMAKE_INSTALL_PREFIX={}'.format(install_dir),
                    '-DCMAKE_BUILD_TYPE=Release',

                    '-DBUILD_SHARED_LIBS=1',

                    '-DPNG_PNG_INCLUDE_DIR=' + self.get_recipe('png', self.ctx).get_build_dir(arch.arch),
                    '-DJPEG_INCLUDE_DIR=' + self.get_recipe('jpeg', self.ctx).get_build_dir(arch.arch),

                    _env=env)
            shprint(sh.make, '-j' + str(cpu_count() + 1), _env=env)

            # make the install so we can get the config header with the other headers
            shprint(sh.make, 'install', _env=env)


recipe = LibLeptonicaRecipe()
