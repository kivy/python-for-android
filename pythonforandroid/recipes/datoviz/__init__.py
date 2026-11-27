import glob
import os
import shutil
from os.path import join

import sh
from pythonforandroid.logger import info, shprint
from pythonforandroid.recipe import PyProjectRecipe, Recipe


class DatovizRecipe(PyProjectRecipe):
    """Build Datoviz (libdatoviz.so + Python ctypes bindings) for Android."""

    name = "datoviz"
    version = "main"
    url = "git+https://github.com/datoviz/datoviz.git"
    depends = ["python3", "numpy", "cglm"]
    patches = ["android_platform.patch"]

    def _find_glslc(self):
        candidates = glob.glob(
            join(self.ctx.ndk_dir, "shader-tools", "*", "glslc*")
        )
        if candidates:
            return candidates[0]
        return shutil.which("glslc")

    def build_arch(self, arch):
        self.install_hostpython_prerequisites(["pyyaml"])
        build_dir = self.get_build_dir(arch.arch)
        cmake_build_dir = join(build_dir, "p4a_cmake_build")
        toolchain = join(
            self.ctx.ndk_dir, "build", "cmake", "android.toolchain.cmake"
        )
        generator = "Ninja" if shutil.which("ninja") else "Unix Makefiles"
        cglm_install_dir = join(
            Recipe.get_recipe("cglm", self.ctx).get_build_dir(arch.arch),
            "installation",
        )

        cmake_args = [
            "-S",
            build_dir,
            "-B",
            cmake_build_dir,
            "-G",
            generator,
            f"-DCMAKE_TOOLCHAIN_FILE={toolchain}",
            f"-DANDROID_ABI={arch.arch}",
            f"-DANDROID_PLATFORM=android-{self.ctx.ndk_api}",
            f"-DCMAKE_PREFIX_PATH={cglm_install_dir}",
            f"-DCMAKE_SHARED_LINKER_FLAGS=-L{join(cglm_install_dir, 'lib')}",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DDVZ_CGLM_SOURCE=SYSTEM",
            "-DDVZ_BUILD_TESTING=OFF",
            "-DDVZ_BUILD_EXAMPLES=OFF",
            "-DDVZ_WITH_GLFW=OFF",
            "-DDVZ_BUILD_GUI=OFF",
            "-DDVZ_ENABLE_CUDA=OFF",
            "-DDVZ_ENABLE_QT_BRIDGE=OFF",
            "-DDVZ_ENABLE_SHADERC=OFF",
            "-DDVZ_WITH_FREETYPE=OFF",
            "-DDVZ_WITH_MSDF_ATLAS=OFF",
            "-DDVZ_KVAZAAR_SOURCE=OFF",
            f"-DPython3_EXECUTABLE={self.real_hostpython_location}",
        ]
        glslc = self._find_glslc()
        if glslc:
            cmake_args.append(f"-DDVZ_GLSLC_EXECUTABLE={glslc}")

        info(f"Configuring datoviz CMake for {arch.arch} (android-{self.ctx.ndk_api})")
        shprint(sh.cmake, *cmake_args)

        nproc = str(os.cpu_count() or 4)
        info(f"Building libdatoviz.so for {arch.arch}")
        shprint(sh.cmake, "--build", cmake_build_dir, "--target", "datoviz", "-j", nproc)

        built_so = join(cmake_build_dir, "src", "libdatoviz.so")
        target_so = join(build_dir, "datoviz", "libdatoviz.so")
        shutil.copy2(built_so, target_so)

        super().build_arch(arch)


recipe = DatovizRecipe()
