from pythonforandroid.toolchain import NDKRecipe
from pythonforandroid.patching import is_arch


class LibSDL2Image(NDKRecipe):
    version = '2.0.0'
    url = 'https://www.libsdl.org/projects/SDL_image/release/SDL2_image-{version}.tar.gz'
    dir_name = 'SDL2_image'

    patches = ['disable_webp.patch',
               ('disable_jpg.patch', is_arch('x86'))]


recipe = LibSDL2Image()
