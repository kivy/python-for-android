import os
import sh
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.util import current_directory


class LibSDL3TTF(BootstrapNDKRecipe):
    version = "3.2.2"
    url = "https://github.com/libsdl-org/SDL_ttf/releases/download/release-{version}/SDL3_ttf-{version}.tar.gz"
    dir_name = "SDL3_ttf"

    def get_include_dirs(self, arch):
        return [
            os.path.join(
                self.ctx.bootstrap.build_dir, "jni", "SDL3_ttf", "include"
            ),
            os.path.join(
                self.ctx.bootstrap.build_dir,
                "jni",
                "SDL3_ttf",
                "include",
                "SDL3_ttf",
            ),
        ]

    def prebuild_arch(self, arch):
        # We do not have a folder for each arch on BootstrapNDKRecipe, so we
        # need to skip the external deps download if we already have done it.
        external_deps_dir = os.path.join(
            self.get_build_dir(arch.arch), "external"
        )
        if not os.path.exists(os.path.join(external_deps_dir, "harfbuzz")):
            with current_directory(external_deps_dir):
                shprint(sh.Command("./download.sh"))
        super().prebuild_arch(arch)


recipe = LibSDL3TTF()
