from pythonforandroid.recipe import CythonRecipe


class MsgPackRecipe(CythonRecipe):
    version = '0.4.7'
    url = 'https://pypi.python.org/packages/source/m/msgpack-python/msgpack-python-{version}.tar.gz'
    depends = ["setuptools"]
    call_hostpython_via_targetpython = False


recipe = MsgPackRecipe()
