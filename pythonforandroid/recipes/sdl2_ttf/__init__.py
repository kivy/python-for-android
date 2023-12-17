from pythonforandroid.recipe import BootstrapNDKRecipe


class LibSDL2TTF(BootstrapNDKRecipe):
    version = '2.20.2'
    url = 'https://github.com/libsdl-org/SDL_ttf/releases/download/release-{version}/SDL2_ttf-{version}.tar.gz'
    dir_name = 'SDL2_ttf'


recipe = LibSDL2TTF()
