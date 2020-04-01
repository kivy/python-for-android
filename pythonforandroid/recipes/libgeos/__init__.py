from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.toolchain import shprint
from pythonforandroid.recipe import Recipe
from multiprocessing import cpu_count
from os.path import join
import sh


class LibgeosRecipe(Recipe):
    version = '3.7.1'
    url = 'https://github.com/libgeos/libgeos/archive/{version}.zip'
    depends = []
    built_libraries = {
        'libgeos.so': 'install_target/lib',
        'libgeos_c.so': 'install_target/lib'
    }
    need_stl_shared = True

    def build_arch(self, arch):
        source_dir = self.get_build_dir(arch.arch)
        build_target = join(source_dir, 'build_target')
        install_target = join(source_dir, 'install_target')

        ensure_dir(build_target)
        with current_directory(build_target):
            env = self.get_recipe_env(arch)
            shprint(sh.cmake, source_dir,
                    '-DANDROID_ABI={}'.format(arch.arch),
                    '-DANDROID_NATIVE_API_LEVEL={}'.format(self.ctx.ndk_api),
                    '-DANDROID_STL=' + self.stl_lib_name,

                    '-DCMAKE_TOOLCHAIN_FILE={}'.format(
                        join(self.ctx.ndk_dir, 'build', 'cmake',
                             'android.toolchain.cmake')),
                    '-DCMAKE_INSTALL_PREFIX={}'.format(install_target),
                    '-DCMAKE_BUILD_TYPE=Release',

                    '-DGEOS_ENABLE_TESTS=OFF',

                    '-DBUILD_SHARED_LIBS=1',

                    _env=env)
            shprint(sh.make, '-j' + str(cpu_count()), _env=env)

            # We make the install because this way we will have all the
            # includes in one place (mostly we are interested in `geos_c.h`,
            # which is not in the include folder, so this way we make easier to
            # link with this library...case of shapely's recipe)
            shprint(sh.make, 'install', _env=env)


recipe = LibgeosRecipe()
