from pythonforandroid.recipe import CythonRecipe


class PyProjRecipe(CythonRecipe):
    version = '1.9.5.1'
    url = 'https://github.com/jswhit/pyproj/archive/master.zip'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False


recipe = PyProjRecipe()
