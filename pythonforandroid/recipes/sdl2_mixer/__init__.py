import os

from pythonforandroid.recipe import BootstrapNDKRecipe


class LibSDL2Mixer(BootstrapNDKRecipe):
    version = '2.6.3'
    url = 'https://github.com/libsdl-org/SDL_mixer/releases/download/release-{version}/SDL2_mixer-{version}.tar.gz'
    dir_name = 'SDL2_mixer'

    def get_include_dirs(self, arch):
        return [
            os.path.join(self.ctx.bootstrap.build_dir, "jni", "SDL2_mixer", "include")
        ]


recipe = LibSDL2Mixer()
