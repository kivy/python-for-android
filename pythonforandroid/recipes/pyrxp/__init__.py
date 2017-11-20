from pythonforandroid.toolchain import CompiledComponentsPythonRecipe, warning
class PyRXPURecipe(CompiledComponentsPythonRecipe):
    version = '2a02cecc87b9'
    url = 'https://bitbucket.org/rptlab/pyrxp/get/{version}.tar.gz'
    depends = ['python2']
    patches = []

recipe = PyRXPURecipe()
