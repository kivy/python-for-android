from pythonforandroid.recipe import PythonRecipe


class PytzRecipe(PythonRecipe):
    name = 'pytz'
    version = '2015.7'
    url = 'https://pypi.python.org/packages/source/p/pytz/pytz-{version}.tar.bz2'

    depends = []

    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = PytzRecipe()
