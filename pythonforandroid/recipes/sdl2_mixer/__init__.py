from pythonforandroid.recipe import BootstrapNDKRecipe


class LibSDL2Mixer(BootstrapNDKRecipe):
    version = '2.0.4'
    url = 'https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-{version}.tar.gz'
    dir_name = 'SDL2_mixer'

    patches = ['toggle_modplug_mikmod_smpeg_ogg.patch']


recipe = LibSDL2Mixer()
