from pythonforandroid.toolchain import NDKRecipe, shprint, current_directory, info
from os.path import exists, join
import sh


class LibSDL2Recipe(NDKRecipe):
    version = "2.0.3"
    url = "https://www.libsdl.org/release/SDL2-{version}.tar.gz"

    dir_name = 'SDL'

    depends = ['python2', 'sdl2_image', 'sdl2_mixer', 'sdl2_ttf']
    conflicts = ['sdl', 'pygame', 'pygame_bootstrap_components']

    patches = ['add_nativeSetEnv.patch']

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, "V=1", _env=env)


recipe = LibSDL2Recipe()

