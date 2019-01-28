from pythonforandroid.recipe import CythonRecipe


class WSAccellRecipe(CythonRecipe):
    version = '0.6.2'
    url = 'https://pypi.python.org/packages/source/w/wsaccel/wsaccel-{version}.tar.gz'
    depends = []
    call_hostpython_via_targetpython = False


recipe = WSAccellRecipe()
