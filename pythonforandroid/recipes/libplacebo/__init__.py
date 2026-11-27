import os
import shutil
import tarfile
import urllib.request
from os.path import exists, join

from pythonforandroid.logger import info, shprint
from pythonforandroid.recipe import MesonRecipe
from pythonforandroid.util import ensure_dir


class LibplaceboRecipe(MesonRecipe):
    version = "7.387.0"
    url = "https://code.videolan.org/videolan/libplacebo/-/archive/v{version}/libplacebo-v{version}.tar.gz"
    depends = []
    skip_python = True
    hostpython_prerequisites = ["jinja2", "glad2"]
    built_libraries = {"libplacebo.so": "installation/lib"}

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        source_dir = self.get_build_dir(arch.arch)
        fast_float_dir = join(source_dir, "src", "include", "fast_float")
        fast_float_h = join(fast_float_dir, "fast_float.h")
        if not exists(fast_float_h):
            ensure_dir(fast_float_dir)
            url = "https://github.com/fastfloat/fast_float/releases/download/v8.2.3/fast_float.h"
            info(f"Downloading fast_float.h for libplacebo from {url}")
            urllib.request.urlretrieve(url, fast_float_h)

        vk_headers_dir = join(source_dir, "3rdparty", "Vulkan-Headers")
        if not exists(join(vk_headers_dir, "include")):
            vk_ver = "1.4.335"
            vk_url = f"https://github.com/KhronosGroup/Vulkan-Headers/archive/refs/tags/v{vk_ver}.tar.gz"
            vk_tgz = join(source_dir, f"Vulkan-Headers-{vk_ver}.tar.gz")
            info(f"Downloading Vulkan-Headers v{vk_ver} for libplacebo")
            urllib.request.urlretrieve(vk_url, vk_tgz)
            with tarfile.open(vk_tgz, "r:gz") as tf:
                tf.extractall(join(source_dir, "3rdparty"))
            shutil.rmtree(vk_headers_dir, ignore_errors=True)
            shutil.move(join(source_dir, "3rdparty", f"Vulkan-Headers-{vk_ver}"), vk_headers_dir)
            os.remove(vk_tgz)

    def get_recipe_meson_options(self, arch):
        options = super().get_recipe_meson_options(arch)
        options["binaries"]["pkgconfig"] = "pkg-config"
        return options

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc=with_flags_in_cc)
        pc_dir = join(self.get_build_dir(arch.arch), "p4a_pkgconfig")
        ensure_dir(pc_dir)
        vulkan_pc = join(pc_dir, "vulkan.pc")
        with open(vulkan_pc, "w", encoding="utf-8") as f:
            f.write(
                f"prefix={self.ctx.ndk.sysroot}/usr\n"
                f"includedir=${{prefix}}/include\n"
                f"libdir={arch.ndk_lib_dir_versioned}\n\n"
                "Name: vulkan\n"
                "Description: Android NDK Vulkan\n"
                "Version: 1.3.0\n"
                "Libs: -L${libdir} -lvulkan\n"
                "Cflags: -I${includedir}\n"
            )
        existing = env.get("PKG_CONFIG_PATH", "")
        env["PKG_CONFIG_PATH"] = f"{pc_dir}:{existing}" if existing else pc_dir
        env["PKG_CONFIG_LIBDIR"] = pc_dir
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
            "-Dvulkan=enabled",
            "-Dvk-proc-addr=enabled",
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
