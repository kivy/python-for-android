from pythonforandroid.recipe import PyProjectRecipe


class PycryptodomeRecipe(PyProjectRecipe):
    version = '3.23.0'
    url = 'https://github.com/Legrandin/pycryptodome/archive/refs/tags/v{version}.tar.gz'
    depends = ['cffi']


recipe = PycryptodomeRecipe()
