from pythonforandroid.toolchain import BootstrapNDKRecipe


class LibSDL2Mixer(BootstrapNDKRecipe):
    version = '2.0.0'
    url = 'https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-{version}.tar.gz'
    dir_name = 'SDL2_mixer'

    patches = ['disable_modplug_mikmod_smpeg.patch']


recipe = LibSDL2Mixer()
