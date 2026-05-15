import os
from os.path import join, dirname, basename
from pythonforandroid.recipe import MesonRecipe, Recipe
from pythonforandroid.logger import warning
from pathlib import Path


class ScipyRecipe(MesonRecipe):

    version = "v1.16.2"
    url = "git+https://github.com/scipy/scipy.git"
    depends = ["numpy", "libopenblas", "fortran"]
    need_stl_shared = True
    meson_version = "1.5.0"
    hostpython_prerequisites = [
        "numpy",
        "Cython>=3.0.8",
        "pybind11>=2.13.2,<3.1.0",
    ]
    patches = ["meson.patch"]

    def get_recipe_meson_options(self, arch):
        options = super().get_recipe_meson_options(arch)
        options["binaries"]["fortran"] = self.place_wrapper(arch)
        options["properties"]["numpy-include-dir"] = join(
            self.ctx.get_python_install_dir(arch.arch), "numpy/_core/include"
        )
        self.ensure_args(
            "-Csetup-args=-Dblas=openblas",
            "-Csetup-args=-Dlapack=openblas",
            f"-Csetup-args=-Dopenblas_libdir={self.ctx.get_libs_dir(arch.arch)}",
            f'-Csetup-args=-Dopenblas_incldir={join(Recipe.get_recipe("libopenblas", self.ctx).get_build_dir(arch.arch), "build")}',
            "-Csetup-args=-Duse-pythran=false",
        )
        return options

    def place_wrapper(self, arch):
        compiler = Recipe.get_recipe("fortran", self.ctx).get_fortran_bin(arch.arch)
        file = join(self.get_recipe_dir(), "wrapper.py")
        with open(file, "r") as _file:
            data = _file.read()
            _file.close()
        data = data.replace("@COMPILER@", compiler)
        # custom compiler
        # taken from: https://github.com/termux/termux-packages/blob/master/packages/python-scipy/
        m_compiler = Path(join(dirname(compiler), basename(compiler) + "-scipy"))
        m_compiler.write_text(data)
        m_compiler.chmod(0o755)
        self.patch_shebang(str(m_compiler), self.real_hostpython_location)
        return str(m_compiler)

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        arch_env = arch.get_env()
        env["LDFLAGS"] = arch_env["LDFLAGS"]
        env["LDFLAGS"] += " -L{} -lpython{}".format(
            self.ctx.python_recipe.link_root(arch.arch),
            self.ctx.python_recipe.link_version,
        )
        return env

    def build_arch(self, arch):
        if arch.arch not in ["arm64-v8a", "x86_64"]:
            warning(
                "SciPy supports only 64-bit Android architectures: arm64-v8a and x86_64; skipping build."
            )
            return

        if os.name != "posix":
            warning("Building SciPy is only supported on Linux; skipping.")
            return

        super().build_arch(arch)


recipe = ScipyRecipe()
