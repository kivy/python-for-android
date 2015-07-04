from pythonforandroid.toolchain import NDKRecipe, shprint
from os.path import exists, join
import sh

class LibSDL2Image(NDKRecipe):
    version = '2.0.0'
    url = 'https://www.libsdl.org/projects/SDL_image/release/SDL2_image-{version}.tar.gz'
    dir_name = 'SDL2_image'
    
    def prebuild_arch(self, arch):
        super(LibSDL2Image, self).prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        if exists(join(build_dir, '.patched')):
            print('SDL2_image already patched, skipping')
            return
        self.apply_patch('disable_webp.patch')
        shprint(sh.touch, join(build_dir, '.patched'))

recipe = LibSDL2Image()
