import os
import sh
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.util import current_directory


class LibSDL2Image(BootstrapNDKRecipe):
    version = '2.8.0'
    url = 'https://github.com/libsdl-org/SDL_image/releases/download/release-{version}/SDL2_image-{version}.tar.gz'
    dir_name = 'SDL2_image'

    patches = ['enable-webp.patch']

    def get_include_dirs(self, arch):
        return [
            os.path.join(self.ctx.bootstrap.build_dir, "jni", "SDL2_image", "include")
        ]

    def prebuild_arch(self, arch):
        # We do not have a folder for each arch on BootstrapNDKRecipe, so we
        # need to skip the external deps download if we already have done it.
        external_deps_dir = os.path.join(self.get_build_dir(arch.arch), "external")
        if not os.path.exists(os.path.join(external_deps_dir, "libwebp")):
            with current_directory(external_deps_dir):
                shprint(sh.Command("./download.sh"))
        super().prebuild_arch(arch)


recipe = LibSDL2Image()
