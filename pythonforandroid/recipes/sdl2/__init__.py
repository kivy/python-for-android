from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.toolchain import current_directory, shprint
import sh


class LibSDL2Recipe(BootstrapNDKRecipe):
    version = "2.0.4"
    url = "https://www.libsdl.org/release/SDL2-{version}.tar.gz"
    md5sum = '44fc4a023349933e7f5d7a582f7b886e'

    dir_name = 'SDL'

    depends = ['sdl2_image', 'sdl2_mixer', 'sdl2_ttf']
    conflicts = ['sdl', 'pygame', 'pygame_bootstrap_components']

    patches = ['add_nativeSetEnv.patch']

    def get_recipe_env(self, arch=None, with_flags_in_cc=True, with_python=True):
        env = super(LibSDL2Recipe, self).get_recipe_env(
            arch=arch, with_flags_in_cc=with_flags_in_cc, with_python=with_python)
        env['APP_ALLOW_MISSING_DEPS'] = 'true'
        return env

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, "V=1", _env=env)


recipe = LibSDL2Recipe()
