from pythonforandroid.recipe import BootstrapNDKRecipe


class LibSDL2TTF(BootstrapNDKRecipe):
    version = '2.0.15'
    url = 'https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-{version}.tar.gz'
    dir_name = 'SDL2_ttf'


recipe = LibSDL2TTF()
