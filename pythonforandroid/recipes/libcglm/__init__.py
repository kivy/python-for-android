import os
import shutil
from os.path import join

import sh

from pythonforandroid.logger import info, shprint
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import ensure_dir


class LibCglmRecipe(Recipe):
    version = "0.9.6"
    url = "https://github.com/recp/cglm/archive/refs/tags/v{version}.tar.gz"
    built_libraries = {
        "libcglm.so": "installation/lib",
    }

    def build_arch(self, arch):
        source_dir = self.get_build_dir(arch.arch)
        build_dir = join(source_dir, "p4a_build")
        install_dir = join(source_dir, "installation")
        toolchain = join(self.ctx.ndk_dir, "build", "cmake", "android.toolchain.cmake")
        generator = "Ninja" if shutil.which("ninja") else "Unix Makefiles"

        ensure_dir(build_dir)
        cmake_args = [
            "-S",
            source_dir,
            "-B",
            build_dir,
            "-G",
            generator,
            f"-DCMAKE_TOOLCHAIN_FILE={toolchain}",
            f"-DANDROID_ABI={arch.arch}",
            f"-DANDROID_PLATFORM=android-{self.ctx.ndk_api}",
            f"-DCMAKE_INSTALL_PREFIX={install_dir}",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
            "-DCGLM_SHARED=ON",
            "-DCGLM_STATIC=OFF",
            "-DCGLM_USE_C99=ON",
            "-DCGLM_USE_TEST=OFF",
        ]
        info(f"Building cglm {self.version} for {arch.arch}")
        shprint(sh.cmake, *cmake_args)
        shprint(sh.cmake, "--build", build_dir, "-j", str(os.cpu_count() or 4))
        shprint(sh.cmake, "--install", build_dir)


recipe = LibCglmRecipe()
