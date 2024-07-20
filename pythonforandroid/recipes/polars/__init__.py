import time
from os.path import join
from glob import glob
from pythonforandroid.logger import warning
from pythonforandroid.recipe import RustCompiledComponentsRecipe

WARNING_MSG = """

This build requires at least 6GB of free RAM. If you cannot arrange free RAM, please consider adding some swap memory.

For Linux:

1. Open a terminal and execute the following commands to create an 8GB swap file:
   sudo fallocate -l 8G /swapfile.swap
   sudo chmod 700 /swapfile.swap
   sudo mkswap /swapfile.swap
   sudo swapon /swapfile.swap

2. To make the swap memory permanent, add it to your system's configuration by executing:
   sudo sh -c 'echo "/swapfile.swap swap swap defaults 0 0" >> /etc/fstab'

Learn more about swap: https://en.wikipedia.org/wiki/Memory_paging
"""


class PolarsRecipe(RustCompiledComponentsRecipe):
    version = "0.20.25"
    url = "https://github.com/pola-rs/polars/releases/download/py-{version}/polars-{version}.tar.gz"
    toolchain = "nightly-2024-04-15"  # from rust-toolchain.toml
    need_stl_shared = True

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        # Required for libz-ng-sys
        env["CMAKE_TOOLCHAIN_FILE"] = join(
            self.ctx.ndk_dir, "build", "cmake", "android.toolchain.cmake")

        # Enable SIMD instructions
        simd_include = glob(join(
            self.ctx.ndk.llvm_prebuilt_dir,
            "lib64",
            "clang",
            "*",
            "include"
        ))[0]
        env["CFLAGS"] += " -D__ARM_FEATURE_SIMD32=1 -I{}".format(simd_include)

        # Required for libgit2-sys
        env["CFLAGS"] += " -I{}".format(self.ctx.ndk.sysroot_include_dir)

        # We don't want rust cc to set flags for us
        env["CRATE_CC_NO_DEFAULTS"] = "1"
        return env

    def build_arch(self, arch):
        warning(WARNING_MSG)
        time.sleep(5)  # let user read the warning

        # Polars doesn't officially support 32-bit Python.
        # See https://github.com/pola-rs/polars/issues/10460
        if arch.arch in ["x86", "armeabi-v7a"]:
            warning("Polars does not support architecture: {}".format(arch.arch))
            return
        else:
            super().build_arch(arch)


recipe = PolarsRecipe()
