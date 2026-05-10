from pythonforandroid.recipe import PyProjectRecipe


class FreetypePyRecipe(PyProjectRecipe):
    version = '2.5.1'
    url = 'https://github.com/rougier/freetype-py/archive/refs/tags/v{version}.tar.gz'
    patches = ["fix_import.patch"]
    depends = ['freetype']
    site_packages_name = 'freetype'

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env["SETUPTOOLS_SCM_PRETEND_VERSION_FOR_freetype_py"] = self.version
        return env


recipe = FreetypePyRecipe()
