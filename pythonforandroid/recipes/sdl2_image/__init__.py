import os
import sh
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import BootstrapNDKRecipe


class LibSDL2Image(BootstrapNDKRecipe):
    version = '2.8.2'
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

        build_dir = self.get_build_dir(arch.arch)

        with open(os.path.join(build_dir, ".gitmodules"), "r") as file:
            for section in file.read().split('[submodule "')[1:]:
                line_split = section.split(" = ")
                # Parse .gitmodule section
                clone_path, url, branch = (
                    os.path.join(build_dir, line_split[1].split("\n")[0].strip()),
                    line_split[2].split("\n")[0].strip(),
                    line_split[-1].strip()
                )
                # Clone if needed
                if not os.path.exists(clone_path) or not os.listdir(clone_path):
                    shprint(
                        sh.git, "clone", url,
                        "--depth", "1", "-b",
                        branch, clone_path, "--recursive"
                    )

        super().prebuild_arch(arch)


recipe = LibSDL2Image()
