from os.path import exists, join

from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.toolchain import current_directory, shprint
import sh


class LibSDL3Recipe(BootstrapNDKRecipe):
    version = "3.2.18"
    url = "https://github.com/libsdl-org/SDL/releases/download/release-{version}/SDL3-{version}.tar.gz"
    md5sum = "70cda886bcf5a4fdac550db796d2efa2"

    conflicts = ["sdl2"]

    dir_name = "SDL"

    depends = ["sdl3_image", "sdl3_mixer", "sdl3_ttf"]

    def get_recipe_env(
        self, arch=None, with_flags_in_cc=True, with_python=True
    ):
        env = super().get_recipe_env(
            arch=arch,
            with_flags_in_cc=with_flags_in_cc,
            with_python=with_python,
        )
        env["APP_ALLOW_MISSING_DEPS"] = "true"
        return env

    def get_include_dirs(self, arch):
        return [
            join(self.ctx.bootstrap.build_dir, "jni", "SDL", "include"),
            join(self.ctx.bootstrap.build_dir, "jni", "SDL", "include", "SDL3"),
        ]

    def should_build(self, arch):
        libdir = join(self.get_build_dir(arch.arch), "../..", "libs", arch.arch)
        libs = [
            "libmain.so",
            "libSDL3.so",
            "libSDL3_image.so",
            "libSDL3_mixer.so",
            "libSDL3_ttf.so",
        ]
        return not all(exists(join(libdir, x)) for x in libs)

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(
                sh.Command(join(self.ctx.ndk_dir, "ndk-build")),
                "V=1",
                "NDK_DEBUG=" + ("1" if self.ctx.build_as_debuggable else "0"),
                _env=env,
            )


recipe = LibSDL3Recipe()
