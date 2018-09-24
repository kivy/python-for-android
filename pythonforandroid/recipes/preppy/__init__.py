from pythonforandroid.recipe import PythonRecipe


class PreppyRecipe(PythonRecipe):
    version = '27b7085'
    url = 'https://bitbucket.org/rptlab/preppy/get/{version}.tar.gz'
    depends = [('python2', 'python3crystax')]
    patches = ['fix-setup.patch']
    call_hostpython_via_targetpython = False


recipe = PreppyRecipe()
