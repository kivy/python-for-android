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
    need_stl_shared = True

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["CXXFLAGS"] += " -Wno-c++11-narrowing"
        return env


recipe = MatplotlibRecipe()
