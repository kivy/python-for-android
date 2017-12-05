from pythonforandroid.recipe import PythonRecipe


class PycryptodomeRecipe(PythonRecipe):
    version = 'v3.4.6'
    url = 'https://github.com/Legrandin/pycryptodome/archive/{version}.tar.gz'

    depends = ['python2', 'setuptools', 'cffi']


recipe = PycryptodomeRecipe()
