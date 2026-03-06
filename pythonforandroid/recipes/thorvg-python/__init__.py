from pythonforandroid.recipe import PyProjectRecipe


class ThorVGPythonRecipe(PyProjectRecipe):
    site_packages_name = "thorvg_python"
    version = "1.1.1"
    url = "https://github.com/laggykiller/thorvg-python/archive/refs/tags/v{version}.tar.gz"
    depends = ["libthorvg"]
    patches = ["sharedlib.patch"]


recipe = ThorVGPythonRecipe()
