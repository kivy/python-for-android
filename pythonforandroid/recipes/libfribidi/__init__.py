from os.path import join

from pythonforandroid.logger import info, shprint
from pythonforandroid.recipe import MesonRecipe
from pythonforandroid.util import ensure_dir


class LibfribidiRecipe(MesonRecipe):
    version = "1.0.18"
    url = "https://github.com/fribidi/fribidi/releases/download/v{version}/fribidi-{version}.tar.xz"
    depends = []
    skip_python = True
    built_libraries = {"libfribidi.so": "installation/lib"}

    def get_recipe_meson_options(self, arch):
        options = super().get_recipe_meson_options(arch)
        options["binaries"]["pkgconfig"] = "pkg-config"
        return options

    def build_arch(self, arch):
        super().build_arch(arch)
        source_dir = self.get_build_dir(arch.arch)
        build_dir = join(source_dir, "p4a_meson_build")
        install_dir = join(source_dir, "installation")
        ensure_dir(build_dir)
        env = self.get_recipe_env(arch, with_flags_in_cc=True)
        meson = self.get_meson_command(env)

        info(f"Configuring fribidi {self.version} for {arch.arch}")
        shprint(
            meson,
            "setup",
            build_dir,
            source_dir,
            "--cross-file",
            "/tmp/android.meson.cross",
            f"--prefix={install_dir}",
            "--libdir=lib",
            "--buildtype=release",
            "-Ddefault_library=shared",
            "-Ddocs=false",
            "-Dtests=false",
            "-Dbin=false",
            _env=env,
        )
        shprint(meson, "compile", "-C", build_dir, _env=env)
        shprint(meson, "install", "-C", build_dir, _env=env)


recipe = LibfribidiRecipe()
