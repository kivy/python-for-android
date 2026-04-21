from pythonforandroid.recipe import MesonRecipe


class MatplotlibRecipe(MesonRecipe):
    version = "3.10.7"
    url = "https://github.com/matplotlib/matplotlib/archive/v{version}.zip"
    depends = ["kiwisolver", "numpy", "pillow"]
    python_depends = [
        "cycler",
        "fonttools",
        "packaging",
        "pyparsing",
        "python-dateutil",
    ]
    pybind_version = "2.13.4"
    hostpython_prerequisites = ["meson-python>=0.13.1,<0.17.0", "pybind11>=2.13.2,!=2.13.3", "setuptools_scm>=7"]
    need_stl_shared = True

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["CXXFLAGS"] += " -Wno-c++11-narrowing"
        return env


recipe = MatplotlibRecipe()
