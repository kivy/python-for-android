from pythonforandroid.recipe import PythonRecipe


class PycryptodomeRecipe(PythonRecipe):
    url = 'https://github.com/Legrandin/pycryptodome/archive/master.zip'

    depends = ['python2', 'setuptools']


recipe = PycryptodomeRecipe()
