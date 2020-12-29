from pythonforandroid.recipe import PythonRecipe


class PycryptodomeRecipe(PythonRecipe):
    version = '20.1.0'
    url = 'https://github.com/hynek/argon2-cffi/archive/master.zip'
    depends = ['cffi']


recipe = PycryptodomeRecipe()
