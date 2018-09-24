from pythonforandroid.recipe import PythonRecipe


class IdnaRecipe(PythonRecipe):
    name = 'idna'
    version = '2.6'
    url = 'https://github.com/kjd/idna/archive/v{version}.tar.gz'

    depends = [('python2', 'python3crystax'), 'setuptools']

    call_hostpython_via_targetpython = False


recipe = IdnaRecipe()
