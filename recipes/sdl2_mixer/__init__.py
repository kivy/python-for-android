
from toolchain import NDKRecipe, shprint
from os.path import exists, join
import sh

class LibSDL2Mixer(NDKRecipe):
    version = '2.0.0'
    url = 'https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-{version}.tar.gz'
    dir_name = 'SDL2_mixer'

    def prebuild_arch(self, arch):
        super(LibSDL2Mixer, self).prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)

        if exists(join(build_dir, '.patched')):
            print('SDL2_mixer already patched, skipping')
            return
        self.apply_patch('disable_modplug_mikmod_smpeg.patch')
        shprint(sh.touch, join(build_dir, '.patched'))

recipe = LibSDL2Mixer()
