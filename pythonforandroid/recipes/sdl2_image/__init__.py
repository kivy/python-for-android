from pythonforandroid.toolchain import BootstrapNDKRecipe
from pythonforandroid.patching import is_arch


class LibSDL2Image(BootstrapNDKRecipe):
    version = '2.0.1'
    url = 'https://www.libsdl.org/projects/SDL_image/release/SDL2_image-{version}.tar.gz'
    dir_name = 'SDL2_image'

    patches = ['toggle_jpg_png_webp.patch',
               ('disable_jpg.patch', is_arch('x86')),
               'extra_cflags.patch',
               'fix_with_ndk_15_plus.patch']

recipe = LibSDL2Image()
