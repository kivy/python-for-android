import shutil
from os.path import join

from pythonforandroid.logger import info, shprint
from pythonforandroid.recipe import MesonRecipe
from pythonforandroid.util import ensure_dir


class LibmpvRecipe(MesonRecipe):
    version = "0.42.0"
    url = "https://github.com/mpv-player/mpv/archive/refs/tags/v{version}.tar.gz"
    depends = ["ffmpeg", "libass", "libplacebo"]
    skip_python = True
    built_libraries = {"libmpv.so": "installation/lib"}

    def get_recipe_meson_options(self, arch):
        options = super().get_recipe_meson_options(arch)
        options["binaries"]["pkgconfig"] = "pkg-config"
        options["properties"].pop("sys_root", None)
        return options

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc=with_flags_in_cc)
        ffmpeg_dir = self.get_recipe("ffmpeg", self.ctx).get_build_dir(arch.arch)
        libass_install = join(
            self.get_recipe("libass", self.ctx).get_build_dir(arch.arch),
            "installation",
        )
        libplacebo_install = join(
            self.get_recipe("libplacebo", self.ctx).get_build_dir(arch.arch),
            "installation",
        )
        fribidi_install = join(
            self.get_recipe("libfribidi", self.ctx).get_build_dir(arch.arch),
            "installation",
        )
        freetype_install = join(
            self.get_recipe("freetype", self.ctx).get_build_dir(arch.arch),
            "install",
        )
        harfbuzz_dir = self.get_recipe("harfbuzz", self.ctx).get_build_dir(arch.arch)

        pkg_paths = [
            join(ffmpeg_dir, "lib", "pkgconfig"),
            join(libass_install, "lib", "pkgconfig"),
            join(libplacebo_install, "lib", "pkgconfig"),
            join(fribidi_install, "lib", "pkgconfig"),
            join(freetype_install, "lib", "pkgconfig"),
            join(harfbuzz_dir, "src"),
        ]
        existing = env.get("PKG_CONFIG_PATH", "")
        env["PKG_CONFIG_PATH"] = ":".join(pkg_paths + ([existing] if existing else []))
        env["PKG_CONFIG_LIBDIR"] = env["PKG_CONFIG_PATH"]
        return env

    def build_arch(self, arch):
        super().build_arch(arch)
        source_dir = self.get_build_dir(arch.arch)
        build_dir = join(source_dir, "p4a_meson_build")
        install_dir = join(source_dir, "installation")
        shutil.rmtree(build_dir, ignore_errors=True)
        ensure_dir(build_dir)
        env = self.get_recipe_env(arch, with_flags_in_cc=True)
        meson = self.get_meson_command(env)

        info(f"Configuring mpv {self.version} for {arch.arch}")
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
            "-Dlibmpv=true",
            "-Dcplayer=false",
            "-Dgl=enabled",
            "-Degl=disabled",
            "-Degl-android=enabled",
            "-Dandroid-media-ndk=enabled",
            "-Dopensles=enabled",
            "-Daaudio=disabled",
            "-Dlua=disabled",
            "-Ddvdnav=disabled",
            "-Dlcms2=disabled",
            "-Dlibbluray=disabled",
            "-Dvapoursynth=disabled",
            "-Dzimg=disabled",
            "-Ddrm=disabled",
            "-Dgbm=disabled",
            "-Djpeg=disabled",
            "-Dvdpau=disabled",
            "-Dvaapi=disabled",
            "-Dvulkan=disabled",
            "-Dwayland=disabled",
            "-Dx11=disabled",
            "-Dx11-clipboard=disabled",
            "-Dxv=disabled",
            "-Dtests=false",
            _env=env,
        )
        shprint(meson, "compile", "-C", build_dir, _env=env)
        shprint(meson, "install", "-C", build_dir, _env=env)


recipe = LibmpvRecipe()
