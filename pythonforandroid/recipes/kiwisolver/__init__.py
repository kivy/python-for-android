from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class KiwiSolverRecipe(CppCompiledComponentsPythonRecipe):
    site_packages_name = 'kiwisolver'
    version = '0.1.3'
    url = 'https://github.com/nucleic/kiwi/archive/master.zip'
    depends = ['setuptools']


recipe = KiwiSolverRecipe()
