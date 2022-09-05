from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class KiwiSolverRecipe(CppCompiledComponentsPythonRecipe):
    site_packages_name = 'kiwisolver'
    version = '1.3.2'
    url = 'https://github.com/nucleic/kiwi/archive/{version}.zip'
    depends = ['cppy']


recipe = KiwiSolverRecipe()
