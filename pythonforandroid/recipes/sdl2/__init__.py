from toolchain import NDKRecipe, shprint, current_directory, info_main
from os.path import exists
import sh



class LibSDL2Recipe(NDKRecipe):
    version = "2.0.3"
    url = "https://www.libsdl.org/release/SDL2-{version}.tar.gz"
    depends = ['python2', 'sdl2_image', 'sdl2_mixer', 'sdl2_ttf']
    # depends = ['python2']
    dir_name = 'SDL'

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, "V=1", _env=env)


recipe = LibSDL2Recipe()

