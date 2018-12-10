from pythonforandroid.recipe import PythonRecipe


class IdnaRecipe(PythonRecipe):
    name = 'idna'
    version = '2.8'
    url = 'https://github.com/kjd/idna/archive/v{version}.tar.gz'

    depends = ['setuptools']

    call_hostpython_via_targetpython = False


recipe = IdnaRecipe()
