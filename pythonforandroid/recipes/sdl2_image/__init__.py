from pythonforandroid.toolchain import BootstrapNDKRecipe
from pythonforandroid.patching import is_arch


class LibSDL2Image(BootstrapNDKRecipe):
    version = '2.0.0'
    url = 'https://www.libsdl.org/projects/SDL_image/release/SDL2_image-{version}.tar.gz'
    dir_name = 'SDL2_image'

    patches = ['disable_webp.patch',
               ('disable_jpg.patch', is_arch('x86')),
               'extra-cflags.patch',
               ('disable-assembler.patch', is_arch('arm64-v8a'))]


recipe = LibSDL2Image()
