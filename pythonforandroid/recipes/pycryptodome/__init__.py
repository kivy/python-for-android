from pythonforandroid.recipe import PythonRecipe


class PycryptodomeRecipe(PythonRecipe):
    version = '3.7.3'
    url = 'https://github.com/Legrandin/pycryptodome/archive/v{version}.tar.gz'
    depends = ['setuptools', 'cffi']


recipe = PycryptodomeRecipe()
