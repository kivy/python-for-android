from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class BitarrayRecipe(CppCompiledComponentsPythonRecipe):
    stl_lib_name = "c++_shared"
    version = "3.0.0"
    url = "https://github.com/ilanschnell/bitarray/archive/refs/tags/{version}.tar.gz"
    depends = ["setuptools"]


recipe = BitarrayRecipe()
