from pythonforandroid.recipe import BootstrapNDKRecipe


class LibSDL2Image(BootstrapNDKRecipe):
    version = '2.0.4'
    url = 'https://www.libsdl.org/projects/SDL_image/release/SDL2_image-{version}.tar.gz'
    dir_name = 'SDL2_image'

    patches = ['toggle_jpg_png_webp.patch',
               'extra_cflags.patch',
               ]


recipe = LibSDL2Image()
