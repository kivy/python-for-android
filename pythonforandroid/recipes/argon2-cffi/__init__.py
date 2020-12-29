from pythonforandroid.recipe import PythonRecipe


class Argon2Recipe(PythonRecipe):
    version = '20.1.0'
    url = 'https://github.com/hynek/argon2-cffi/archive/master.zip'
    depends = ['setuptools', 'cffi']


recipe = Argon2Recipe()
