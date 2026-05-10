from pythonforandroid.recipe import Recipe, MesonRecipe
from os.path import join, exists
from pythonforandroid.util import ensure_dir, current_directory
from pythonforandroid.logger import shprint
from multiprocessing import cpu_count
import sh


class LibCairoRecipe(MesonRecipe):
    name = 'libcairo'
    version = '1.18.4'
    url = 'https://gitlab.freedesktop.org/cairo/cairo/-/archive/{version}/cairo-{version}.tar.bz2'
    skip_python = True
    depends = ["png", "freetype"]
    patches = ["meson.patch"]
    built_libraries = {
        'libcairo.so': 'install/lib',
        'libpixman-1.so': 'install/lib',
        'libcairo-script-interpreter.so': 'install/lib'
    }

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        cpufeatures = join(self.ctx.ndk.ndk_dir, "sources/android/cpufeatures")
        lib_dir = join(cpufeatures, "obj", "local", arch.arch)
        env["CFLAGS"] += f" -I{cpufeatures}"
        env["LDFLAGS"] += f" -L{lib_dir} -lcpufeatures"
        return env

    def should_build(self, arch):
        return Recipe.should_build(self, arch)

    def build_arch(self, arch):
        super().build_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        install_dir = join(build_dir, 'install')
        ensure_dir(install_dir)
        env = self.get_recipe_env(arch)

        lib_dir = self.ctx.get_libs_dir(arch.arch)
        png_include = self.get_recipe('png', self.ctx).get_build_dir(arch.arch)
        freetype_inc = join(self.get_recipe('freetype', self.ctx).get_build_dir(arch), "include")

        with current_directory(build_dir):

            cpufeatures_dir = join(self.ctx.ndk.ndk_dir, "sources/android/cpufeatures")
            lib_file = join(cpufeatures_dir, "obj", "local", arch.arch, "libcpufeatures.a")

            if not exists(lib_file):
                shprint(
                    sh.Command(join(self.ctx.ndk_dir, "ndk-build")),
                    f"NDK_PROJECT_PATH={cpufeatures_dir}",
                    f"APP_BUILD_SCRIPT={cpufeatures_dir}/Android.mk",
                    f"APP_ABI={arch.arch}",
                    "APP_PLATFORM=latest",
                    _env=env
                )

            shprint(sh.meson, 'setup', 'builddir',
                    '--cross-file', join("/tmp", "android.meson.cross"),
                    f'--prefix={install_dir}',
                    '-Dpng=enabled',
                    '-Dzlib=enabled',
                    '-Dglib=disabled',
                    '-Dgtk_doc=false',
                    '-Dsymbol-lookup=disabled',

                    # deps
                    f'-Dpng_include_dir={png_include}',
                    f'-Dpng_lib_dir={lib_dir}',
                    f'-Dfreetype_include_dir={freetype_inc}',
                    f'-Dfreetype_lib_dir={lib_dir}',
                    _env=env)

            shprint(sh.ninja, '-C', 'builddir', '-j', str(cpu_count()), _env=env)
            # macOS fix: sometimes Ninja creates a dummy 'lib' file instead of a directory.
            # So we remove and recreate the install directory using shell commands,
            # since os.remove/os.makedirs behave inconsistently in this build env.
            shprint(sh.rm, '-rf', install_dir)
            shprint(sh.mkdir, install_dir)

            shprint(sh.ninja, '-C', 'builddir', 'install', _env=env)


recipe = LibCairoRecipe()
