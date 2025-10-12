from pythonforandroid.recipe import MesonRecipe
from pythonforandroid.logger import shprint

from os.path import join
import sh


class MatplotlibRecipe(MesonRecipe):
    version = '3.10.7'
    url = 'https://github.com/matplotlib/matplotlib/archive/v{version}.zip'
    depends = ['kiwisolver', 'numpy', 'pillow']
    python_depends = ['cycler', 'fonttools', 'packaging', 'pyparsing', 'python-dateutil']
    hostpython_prerequisites = ["setuptools_scm>=7"]
    patches = ["meson.patch"]
    need_stl_shared = True

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env['CXXFLAGS'] += ' -Wno-c++11-narrowing'
        return env

    def build_arch(self, arch):
        python_path = join(self.ctx.python_recipe.get_build_dir(arch), "android-build", "python3")
        self.extra_build_args += [f'-Csetup-args=-Dpython3_program={python_path}']
        shprint(sh.cp, self.real_hostpython_location, python_path)
        super().build_arch(arch)


recipe = MatplotlibRecipe()
