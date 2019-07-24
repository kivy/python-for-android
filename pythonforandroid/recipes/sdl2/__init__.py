from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.toolchain import current_directory, shprint
import sh


class LibSDL2Recipe(BootstrapNDKRecipe):
    version = "2.0.10"
    url = "https://www.libsdl.org/release/SDL2-{version}.zip"
    md5sum = "6b2e9a4a2faba4ff277062cf669724f4"

    dir_name = 'SDL'

    depends = ['sdl2_image', 'sdl2_mixer', 'sdl2_ttf']

    def get_recipe_env(self, arch=None, with_flags_in_cc=True, with_python=True):
        env = super().get_recipe_env(
            arch=arch, with_flags_in_cc=with_flags_in_cc, with_python=with_python)
        env['APP_ALLOW_MISSING_DEPS'] = 'true'
        return env

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(
                sh.ndk_build,
                "V=1",
                "NDK_DEBUG=" + ("1" if self.ctx.build_as_debuggable else "0"),
                _env=env
            )


recipe = LibSDL2Recipe()
