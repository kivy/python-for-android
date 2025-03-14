from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class EnamlRecipe(CppCompiledComponentsPythonRecipe):
    site_packages_name = 'enaml'
    version = '0.18.0'
    url = 'https://github.com/nucleic/enaml/archive/refs/tags/{version}.zip'
    depends = ['setuptools', 'atom', 'kiwisolver']


recipe = EnamlRecipe()
