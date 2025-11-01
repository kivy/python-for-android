from pythonforandroid.recipe import PyProjectRecipe


class MaterialyoucolorRecipe(PyProjectRecipe):
    stl_lib_name = "c++_shared"
    version = "2.0.10"
    url = "https://github.com/T-Dynamos/materialyoucolor-python/releases/download/v{version}/materialyoucolor-{version}.tar.gz"

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env['LDCXXSHARED'] = env['CXX'] + ' -shared'
        return env


recipe = MaterialyoucolorRecipe()
