from pythonforandroid.recipe import Recipe, MesonRecipe
from os.path import join
from pythonforandroid.util import ensure_dir, current_directory
from pythonforandroid.logger import shprint
from multiprocessing import cpu_count
from glob import glob
import sh


class LibThorVGRecipe(MesonRecipe):
    name = "libthorvg"
    version = "1.0.5"
    url = "https://github.com/thorvg/thorvg/archive/refs/tags/v{version}.tar.gz"
    config_otps = [
        "-Dsimd=true",
        "-Dbindings=capi",
        "-Dtools=all",
        "-Dengines=cpu,gl",
        "-Dloaders=svg,png,jpg,ttf,webp",
        "-Dextra=opengl_es,lottie_exp,openmp",
    ]
    need_stl_shared = True
    skip_python = True
    depends = ["png", "libwebp", "jpeg"]
    patches = ["meson.patch"]
    bins = ["tvg-lottie2gif", "tvg-svg2png"]
    built_libraries = {
        "libthorvg-1.so": "install/lib",
        "libomp.so": "install/lib"
    }
    for bin in bins:
        built_libraries[f"lib{bin}bin.so"] = "install/bin"

    def should_build(self, arch):
        return Recipe.should_build(self, arch)

    def get_include_dir(self, arch):
        return join(self.get_build_dir(arch.arch), "install", "include")

    def build_arch(self, arch):
        super().build_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        install_dir = join(build_dir, "install")
        ensure_dir(install_dir)
        env = self.get_recipe_env(arch)

        lib_dir = self.ctx.get_libs_dir(arch.arch)
        png_include = self.get_recipe("png", self.ctx).get_build_dir(arch.arch)
        webp_include = join(
            self.get_recipe("libwebp", self.ctx).get_build_dir(arch.arch), "src"
        )
        jpg_dir = self.get_recipe("jpeg", self.ctx).get_build_dir(arch.arch)

        with current_directory(build_dir):

            shprint(
                sh.meson,
                "setup",
                "builddir",
                "--cross-file",
                join("/tmp", "android.meson.cross"),
                f"--prefix={install_dir}",
                # config opts
                *self.config_otps,
                # deps
                f"-Dpng_include_dir={png_include}",
                f"-Dpng_lib_dir={lib_dir}",
                f"-Dwebp_include_dir={webp_include}",
                f"-Dwebp_lib_dir={lib_dir}",
                f"-Djpg_include_dir={jpg_dir}",
                f"-Djpg_lib_dir={jpg_dir}",
                _env=env,
            )

            shprint(sh.ninja, "-C", "builddir", "-j", str(cpu_count()), _env=env)
            shprint(sh.rm, "-rf", install_dir)
            shprint(sh.mkdir, install_dir)
            shprint(sh.ninja, "-C", "builddir", "install", _env=env)

            # copy libomp.so
            arch_map = {
                "arm64-v8a": "aarch64",
                "armeabi-v7a": "arm",
                "x86": "i386",
                "x86_64": "x86_64",
            }
            lib_arch = arch_map[arch.arch]
            # clang version directory is variable, so glob it
            pattern = join(self.ctx.ndk.llvm_prebuilt_dir, "lib/clang/*/lib/linux", lib_arch)
            clang_lib_dir = glob(pattern)[0]
            libomp = join(clang_lib_dir, "libomp.so")
            shprint(sh.cp, libomp, join("install", "lib"))

            # setup bins
            bin_dir = join("install", "bin")
            for bin in self.bins:
                shprint(sh.cp, join(bin_dir, bin), join(bin_dir, f"lib{bin}bin.so"))


recipe = LibThorVGRecipe()
