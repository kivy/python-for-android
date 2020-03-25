from pythonforandroid.recipe import PythonRecipe


class PytzRecipe(PythonRecipe):
    name = 'pytz'
    version = '2019.3'
    url = 'https://pypi.python.org/packages/source/p/pytz/pytz-{version}.tar.gz'

    depends = []

    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = PytzRecipe()
