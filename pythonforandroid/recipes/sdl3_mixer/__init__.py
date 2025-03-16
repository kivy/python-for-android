import os
import sh
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.util import current_directory


class LibSDL3Mixer(BootstrapNDKRecipe):
    version = "72a73339731a12c1002f9caca64f1ab924938102"
    # url = "https://github.com/libsdl-org/SDL_ttf/releases/download/release-{version}/SDL3_ttf-{version}.tar.gz"
    url = "https://github.com/libsdl-org/SDL_mixer/archive/{version}.tar.gz"
    dir_name = "SDL3_mixer"

    patches = ["disable-libgme.patch"]

    def get_include_dirs(self, arch):
        return [
            os.path.join(
                self.ctx.bootstrap.build_dir, "jni", "SDL3_mixer", "include"
            ),
            os.path.join(
                self.ctx.bootstrap.build_dir,
                "jni",
                "SDL3_mixer",
                "include",
                "SDL3_mixer",
            ),
        ]

    def prebuild_arch(self, arch):
        # We do not have a folder for each arch on BootstrapNDKRecipe, so we
        # need to skip the external deps download if we already have done it.
        external_deps_dir = os.path.join(
            self.get_build_dir(arch.arch), "external"
        )

        if not os.path.exists(
            os.path.join(external_deps_dir, "libgme", "Android.mk")
        ):
            with current_directory(external_deps_dir):
                shprint(sh.Command("./download.sh"))
        super().prebuild_arch(arch)


recipe = LibSDL3Mixer()
