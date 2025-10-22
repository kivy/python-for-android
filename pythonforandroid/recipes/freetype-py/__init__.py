from pythonforandroid.recipe import PythonRecipe


class FreetypePyRecipe(PythonRecipe):
    version = '2.2.0'
    url = 'https://github.com/rougier/freetype-py/archive/refs/tags/v{version}.tar.gz'
    depends = ['freetype']
    site_packages_name = 'freetype'


recipe = FreetypePyRecipe()
