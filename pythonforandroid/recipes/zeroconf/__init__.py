from pythonforandroid.recipe import PythonRecipe


class ZeroconfRecipe(PythonRecipe):
    name = 'zeroconf'
    version = '0.17.4'
    url = 'https://pypi.python.org/packages/source/z/zeroconf/zeroconf-{version}.tar.gz'
    depends = ['setuptools', 'enum34', 'six']
    call_hostpython_via_targetpython = False


recipe = ZeroconfRecipe()
