from pythonforandroid.recipe import PyProjectRecipe


class CppyRecipe(PyProjectRecipe):
    site_packages_name = 'cppy'
    version = '1.3.1'
    url = 'https://github.com/nucleic/cppy/archive/refs/tags/{version}.zip'
    call_hostpython_via_targetpython = False
    depends = ['setuptools']

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["SETUPTOOLS_SCM_PRETEND_VERSION_FOR_CPPY"] = self.version
        return env


recipe = CppyRecipe()
