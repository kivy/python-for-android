from pythonforandroid.recipe import PyProjectRecipe


class MaterialyoucolorRecipe(PyProjectRecipe):
    stl_lib_name = "c++_shared"
    version = "3.0.4"
    url = "https://github.com/T-Dynamos/materialyoucolor-python/releases/download/v{version}/materialyoucolor-{version}.tar.gz"


recipe = MaterialyoucolorRecipe()
