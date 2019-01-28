from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class PyRXPURecipe(CompiledComponentsPythonRecipe):
    version = '2a02cecc87b9'
    url = 'https://bitbucket.org/rptlab/pyrxp/get/{version}.tar.gz'
    depends = []
    patches = []


recipe = PyRXPURecipe()
