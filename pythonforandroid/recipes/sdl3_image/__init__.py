import os
import sh
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.util import current_directory


class LibSDL3Image(BootstrapNDKRecipe):
    version = "3.2.4"
    url = "https://github.com/libsdl-org/SDL_image/releases/download/release-{version}/SDL3_image-{version}.tar.gz"
    dir_name = "SDL3_image"

    patches = ["enable-webp.patch"]

    def get_include_dirs(self, arch):
        return [
            os.path.join(
                self.ctx.bootstrap.build_dir, "jni", "SDL3_image", "include"
            ),
            os.path.join(
                self.ctx.bootstrap.build_dir,
                "jni",
                "SDL3_image",
                "include",
                "SDL3_image",
            ),
        ]

    def prebuild_arch(self, arch):
        # We do not have a folder for each arch on BootstrapNDKRecipe, so we
        # need to skip the external deps download if we already have done it.
        external_deps_dir = os.path.join(
            self.get_build_dir(arch.arch), "external"
        )
        if not os.path.exists(os.path.join(external_deps_dir, "libwebp")):
            with current_directory(external_deps_dir):
                shprint(sh.Command("./download.sh"))
        super().prebuild_arch(arch)


recipe = LibSDL3Image()
