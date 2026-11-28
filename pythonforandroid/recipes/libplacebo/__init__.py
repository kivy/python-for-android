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

    def get_pkgconfig_dir(self, arch):
        return join(self.get_build_dir(arch.arch), "p4a_pkgconfig")

    def write_vulkan_pc(self, arch):
        pc_dir = self.get_pkgconfig_dir(arch)
        ensure_dir(pc_dir)
        vulkan_pc = join(pc_dir, "vulkan.pc")
        vk_headers_inc = join(
            self.get_build_dir(arch.arch), "3rdparty", "Vulkan-Headers", "include"
        )
        with open(vulkan_pc, "w", encoding="utf-8") as f:
            f.write(
                f"prefix={self.ctx.ndk.sysroot}/usr\n"
                f"includedir=${{prefix}}/include\n"
                f"libdir={arch.ndk_lib_dir_versioned}\n\n"
                "Name: vulkan\n"
                "Description: Android NDK Vulkan\n"
                "Version: 1.4.335\n"
                "Libs: -L${libdir} -lvulkan\n"
                f"Cflags: -I{vk_headers_inc} -I${{includedir}}\n"
            )

    def get_recipe_meson_options(self, arch):
        options = super().get_recipe_meson_options(arch)
        options["binaries"]["pkgconfig"] = "pkg-config"
        return options

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc=with_flags_in_cc)
        pc_dir = self.get_pkgconfig_dir(arch)
        existing = env.get("PKG_CONFIG_PATH", "")
        env["PKG_CONFIG_PATH"] = f"{pc_dir}:{existing}" if existing else pc_dir
        env["PKG_CONFIG_LIBDIR"] = pc_dir
        return env

    def build_arch(self, arch):
        super().build_arch(arch)
        self.write_vulkan_pc(arch)
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
