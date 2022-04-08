from pythonforandroid.recipe import NDKRecipe
from pythonforandroid.toolchain import current_directory, shprint
from os.path import join
import sh


class OpenALRecipe(NDKRecipe):
    version = '1.21.1'
    url = 'https://github.com/kcat/openal-soft/archive/refs/tags/{version}.tar.gz'

    generated_libraries = ['libopenal.so']

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            cmake_args = [
                "-DANDROID_STL=" + self.stl_lib_name,
                "-DCMAKE_TOOLCHAIN_FILE={}".format(
                    join(self.ctx.ndk_dir, "build", "cmake", "android.toolchain.cmake")
                ),
            ]
            shprint(
                sh.cmake, '.',
                *cmake_args,
                _env=env
            )
            shprint(sh.make, _env=env)
            self.install_libs(arch, 'libopenal.so')


recipe = OpenALRecipe()
