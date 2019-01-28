import os
import sh
from os.path import join
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.toolchain import shprint, info


class PyICURecipe(CompiledComponentsPythonRecipe):
    version = '1.9.2'
    url = 'https://pypi.python.org/packages/source/P/PyICU/PyICU-{version}.tar.gz'
    depends = ["icu"]
    patches = ['locale.patch', 'icu.patch']

    def get_recipe_env(self, arch):
        env = super(PyICURecipe, self).get_recipe_env(arch)

        icu_include = join(
            self.ctx.get_python_install_dir(), "include", "icu")

        env["CC"] += " -I"+icu_include

        include = (
            " -I{ndk}/sources/cxx-stl/gnu-libstdc++/{version}/include/"
            " -I{ndk}/sources/cxx-stl/gnu-libstdc++/{version}/libs/"
            "{arch}/include")
        include = include.format(ndk=self.ctx.ndk_dir,
                                 version=env["TOOLCHAIN_VERSION"],
                                 arch=arch.arch)
        env["CC"] += include

        lib = "{ndk}/sources/cxx-stl/gnu-libstdc++/{version}/libs/{arch}"
        lib = lib.format(ndk=self.ctx.ndk_dir,
                         version=env["TOOLCHAIN_VERSION"],
                         arch=arch.arch)
        env["LDFLAGS"] += " -lgnustl_shared -L"+lib

        build_dir = self.get_build_dir(arch.arch)
        env["LDFLAGS"] += " -L"+build_dir
        return env

    def build_arch(self, arch):
        build_dir = self.get_build_dir(arch.arch)

        info("create links to icu libs")
        lib_dir = join(self.ctx.get_python_install_dir(), "lib")
        icu_libs = [f for f in os.listdir(lib_dir) if f.startswith("libicu")]

        for l in icu_libs:
            raw = l.rsplit(".", 1)[0]
            try:
                shprint(sh.ln, "-s", join(lib_dir, l), join(build_dir, raw))
            except Exception:
                pass

        super(PyICURecipe, self).build_arch(arch)


recipe = PyICURecipe()
