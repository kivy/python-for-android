import shutil
from os.path import join

from pythonforandroid.logger import info, shprint
from pythonforandroid.recipe import MesonRecipe
from pythonforandroid.util import ensure_dir


class LibplaceboRecipe(MesonRecipe):
    version = "v7.387.0"
    url = "git+https://code.videolan.org/videolan/libplacebo.git"
    depends = []
    skip_python = True
    hostpython_prerequisites = ["jinja2>=3.1,<4", "glad2>=2.0,<3"]
    built_libraries = {"libplacebo.so": "installation/lib"}

    def get_recipe_meson_options(self, arch):
        options = super().get_recipe_meson_options(arch)
        options["binaries"]["pkgconfig"] = "pkg-config"
        return options

    def build_arch(self, arch):
        super().build_arch(arch)
        source_dir = self.get_build_dir(arch.arch)
        build_dir = join(source_dir, "p4a_meson_build")
        install_dir = join(source_dir, "installation")
        shutil.rmtree(build_dir, ignore_errors=True)
        ensure_dir(build_dir)
        env = self.get_recipe_env(arch, with_flags_in_cc=True)
        meson = self.get_meson_command(env)

        info(f"Configuring libplacebo {self.version} for {arch.arch}")
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
            "-Dopengl=enabled",
            "-Dvulkan=disabled",
            "-Dvk-proc-addr=disabled",
            "-Dglslang=disabled",
            "-Dshaderc=disabled",
            "-Dlcms=disabled",
            "-Dlibdovi=disabled",
            "-Dd3d11=disabled",
            "-Dtests=false",
            "-Ddemos=false",
            "-Dxxhash=disabled",
            "-Dunwind=disabled",
            _env=env,
        )
        shprint(meson, "compile", "-C", build_dir, _env=env)
        shprint(meson, "install", "-C", build_dir, _env=env)


recipe = LibplaceboRecipe()
