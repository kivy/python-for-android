from toolchain import NDKRecipe
from os.path import exists

class LibSDL2TTF(NDKRecipe):
    version = '2.0.12'
    url = 'https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-{version}.tar.gz'
    dir_name = 'SDL2_ttf'

recipe = LibSDL2TTF()
