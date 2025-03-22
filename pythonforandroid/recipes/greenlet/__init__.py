from pythonforandroid.recipe import PyProjectRecipe


class GreenletRecipe(PyProjectRecipe):
    version = '3.1.1'
    url = 'https://pypi.python.org/packages/source/g/greenlet/greenlet-{version}.tar.gz'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False


recipe = GreenletRecipe()
