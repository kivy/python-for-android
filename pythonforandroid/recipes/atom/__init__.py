from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class AtomRecipe(CppCompiledComponentsPythonRecipe):
    site_packages_name = 'atom'
    version = '0.3.10'
    url = 'https://github.com/nucleic/atom/archive/master.zip'
    depends = ['setuptools']


recipe = AtomRecipe()
