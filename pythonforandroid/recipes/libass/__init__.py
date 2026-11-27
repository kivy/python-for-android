from multiprocessing import cpu_count
from os.path import join

import sh
from pythonforandroid.logger import info, shprint
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory


class LibassRecipe(Recipe):
    version = "0.17.5"
    url = "https://github.com/libass/libass/releases/download/{version}/libass-{version}.tar.xz"
    depends = ["fribidi", "freetype", "harfbuzz"]
    built_libraries = {"libass.so": "installation/lib"}

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)

        fribidi_install = join(
            self.get_recipe("fribidi", self.ctx).get_build_dir(arch.arch),
            "installation",
        )
        freetype_install = join(
            self.get_recipe("freetype", self.ctx).get_build_dir(arch.arch),
            "install",
        )
        harfbuzz_dir = self.get_recipe("harfbuzz", self.ctx).get_build_dir(arch.arch)

        env["FRIBIDI_CFLAGS"] = f"-I{join(fribidi_install, 'include', 'fribidi')}"
        env["FRIBIDI_LIBS"] = f"-L{join(fribidi_install, 'lib')} -lfribidi"
        env["FREETYPE_CFLAGS"] = f"-I{join(freetype_install, 'include', 'freetype2')}"
        env["FREETYPE_LIBS"] = f"-L{join(freetype_install, 'lib')} -lfreetype"
        env["HARFBUZZ_CFLAGS"] = f"-I{join(harfbuzz_dir, 'src')}"
        env["HARFBUZZ_LIBS"] = f"-L{join(harfbuzz_dir, 'src', '.libs')} -lharfbuzz"
        env["PKG_CONFIG_LIBDIR"] = ""
        env["PKG_CONFIG_PATH"] = ""
        return env

    def build_arch(self, arch):
        source_dir = self.get_build_dir(arch.arch)
        install_dir = join(source_dir, "installation")
        env = self.get_recipe_env(arch)

        with current_directory(source_dir):
            info(f"Configuring libass {self.version} for {arch.arch}")
            shprint(
                sh.Command("./configure"),
                f"--host={arch.command_prefix}",
                f"--prefix={install_dir}",
                "--enable-shared",
                "--disable-static",
                "--disable-fontconfig",
                "--disable-require-system-font-provider",
                "--disable-libunibreak",
                "--disable-asm",
                _env=env,
            )
            shprint(sh.make, "-j", str(cpu_count()), _env=env)
            shprint(sh.make, "install", _env=env)


recipe = LibassRecipe()
