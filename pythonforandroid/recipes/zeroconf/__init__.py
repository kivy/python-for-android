from pythonforandroid.recipe import PythonRecipe


class ZeroconfRecipe(PythonRecipe):
    name = 'zeroconf'
    version = '0.24.5'
    url = 'https://pypi.python.org/packages/source/z/zeroconf/zeroconf-{version}.tar.gz'
    depends = ['setuptools', 'ifaddr']
    call_hostpython_via_targetpython = False


recipe = ZeroconfRecipe()
