from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory, ensure_dir
from multiprocessing import cpu_count
from os.path import join
import sh
from pythonforandroid.util import rmdir


class LibOpenBlasRecipe(Recipe):

    version = "0.3.29"
    url = "https://github.com/OpenMathLib/OpenBLAS/archive/refs/tags/v{version}.tar.gz"
    built_libraries = {"libopenblas.so": "build/lib"}
    min_ndk_api_support = 24  # complex math functions support

    def build_arch(self, arch):
        source_dir = self.get_build_dir(arch.arch)
        build_target = join(source_dir, "build")

        ensure_dir(build_target)
        with current_directory(build_target):
            env = self.get_recipe_env(arch)
            rmdir("CMakeFiles")
            shprint(sh.rm, "-f", "CMakeCache.txt", _env=env)

            opts = [
                # default cmake options
                "-DCMAKE_SYSTEM_NAME=Android",
                "-DCMAKE_ANDROID_ARCH_ABI={arch}".format(arch=arch.arch),
                "-DCMAKE_ANDROID_NDK=" + self.ctx.ndk_dir,
                "-DCMAKE_ANDROID_API={api}".format(api=self.ctx.ndk_api),
                "-DCMAKE_BUILD_TYPE=Release",
                "-DBUILD_SHARED_LIBS=ON",
                "-DC_LAPACK=ON",
                "-DTARGET={target}".format(
                    target={
                        "arm64-v8a": "ARMV8",
                        "armeabi-v7a": "ARMV7",
                        "x86_64": "CORE2",
                        "x86": "CORE2",
                    }[arch.arch]
                ),
            ]

            shprint(sh.cmake, source_dir, *opts, _env=env)
            shprint(sh.make, "-j" + str(cpu_count()), _env=env)


recipe = LibOpenBlasRecipe()
