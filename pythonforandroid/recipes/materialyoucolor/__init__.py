from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class MaterialyoucolorRecipe(CompiledComponentsPythonRecipe):
    need_stl_shared = True
    stl_lib_name = "c++_shared"
    version = "2.0.5"
    url = "https://github.com/T-Dynamos/materialyoucolor-pyhton/archive/refs/tags/v{version}.tar.gz"
    depends = ["setuptools"]
    call_hostpython_via_targetpython = False


recipe = MaterialyoucolorRecipe()
