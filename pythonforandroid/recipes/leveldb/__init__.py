from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
from pythonforandroid.recipe import Recipe
from multiprocessing import cpu_count
from os.path import join
import sh


class LevelDBRecipe(Recipe):
    version = '1.22'
    url = 'https://github.com/google/leveldb/archive/{version}.tar.gz'
    depends = ['snappy']
    built_libraries = {'libleveldb.so': '.'}
    need_stl_shared = True

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        source_dir = self.get_build_dir(arch.arch)
        with current_directory(source_dir):
            snappy_recipe = self.get_recipe('snappy', self.ctx)
            snappy_build = snappy_recipe.get_build_dir(arch.arch)

            shprint(sh.cmake, source_dir,
                    '-DANDROID_ABI={}'.format(arch.arch),
                    '-DANDROID_NATIVE_API_LEVEL={}'.format(self.ctx.ndk_api),
                    '-DANDROID_STL=' + self.stl_lib_name,

                    '-DCMAKE_TOOLCHAIN_FILE={}'.format(
                        join(self.ctx.ndk_dir, 'build', 'cmake',
                             'android.toolchain.cmake')),
                    '-DCMAKE_BUILD_TYPE=Release',

                    '-DBUILD_SHARED_LIBS=1',

                    '-DHAVE_SNAPPY=1',
                    '-DCMAKE_CXX_FLAGS=-I{path}'.format(path=snappy_build),
                    '-DCMAKE_SHARED_LINKER_FLAGS=-L{path} -lsnappy'.format(
                        path=snappy_build),
                    '-DCMAKE_EXE_LINKER_FLAGS=-L{path} -lsnappy'.format(
                        path=snappy_build),

                    _env=env)
            shprint(sh.make, '-j' + str(cpu_count()), _env=env)


recipe = LevelDBRecipe()
