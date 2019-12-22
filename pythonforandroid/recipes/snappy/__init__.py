from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
from os.path import join
import sh


class SnappyRecipe(Recipe):
    version = '1.1.7'
    url = 'https://github.com/google/snappy/archive/{version}.tar.gz'
    built_libraries = {'libsnappy.so': '.'}

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        source_dir = self.get_build_dir(arch.arch)
        with current_directory(source_dir):
            shprint(sh.cmake, source_dir,
                    '-DANDROID_ABI={}'.format(arch.arch),
                    '-DANDROID_NATIVE_API_LEVEL={}'.format(self.ctx.ndk_api),
                    '-DCMAKE_TOOLCHAIN_FILE={}'.format(
                        join(self.ctx.ndk_dir, 'build', 'cmake',
                             'android.toolchain.cmake')),
                    '-DBUILD_SHARED_LIBS=1',
                    _env=env)
            shprint(sh.make, _env=env)


recipe = SnappyRecipe()
