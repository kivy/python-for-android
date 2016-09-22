from os.path import join

import sh

from pythonforandroid.logger import shprint
from pythonforandroid.toolchain import BootstrapNDKRecipe


class LibSDL2Mixer(BootstrapNDKRecipe):
    version = '2.0.1'
    url = 'https://www.libsdl.org/projects/SDL_mixer/release/SDL2_mixer-{version}.tar.gz'
    dir_name = 'SDL2_mixer'

    patches = ['toggle_modplug_mikmod_ogg.patch']

    def _external_dir(self):
        """
        Returns the external/ dir path.
        """
        return join(self.get_build_dir(None), 'external')

    def _smpeg2_external_dir(self):
        """
        Returns the smpeg2 external dir path.
        """
        return join(self._external_dir(), 'smpeg2-2.0.0')

    def _copy_smpeg2_to_jni(self):
        """
        Copies the smpeg2 external to the jni/ folder.
        """
        smpeg2_external_dir = self._smpeg2_external_dir()
        jni_dir = self.get_jni_dir()
        shprint(sh.cp, '-r', smpeg2_external_dir, jni_dir)

    def prebuild_arch(self, arch):
        """
        Copies the smpeg2 external library to the jni/ folder.
        This is required by the linker.
        """
        self._copy_smpeg2_to_jni()
        super(LibSDL2Mixer, self).prebuild_arch(arch)

recipe = LibSDL2Mixer()
