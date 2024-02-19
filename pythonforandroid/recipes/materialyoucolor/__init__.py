from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class MaterialyoucolorRecipe(CppCompiledComponentsPythonRecipe):
    stl_lib_name = "c++_shared"
    version = "2.0.7"
    url = "https://github.com/T-Dynamos/materialyoucolor-pyhton/archive/refs/tags/v{version}.tar.gz"
    depends = ["setuptools"]


recipe = MaterialyoucolorRecipe()
