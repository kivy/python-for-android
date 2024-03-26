from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class MaterialyoucolorRecipe(CppCompiledComponentsPythonRecipe):
    stl_lib_name = "c++_shared"
    version = "2.0.9"
    url = "https://github.com/T-Dynamos/materialyoucolor-python/releases/download/v{version}/materialyoucolor-{version}.tar.gz"
    depends = ["setuptools"]


recipe = MaterialyoucolorRecipe()
