from pythonforandroid.recipe import PythonRecipe


class Pysha3Recipe(PythonRecipe):
    version = '1.0.2'

    url = 'https://github.com/tiran/pysha3/archive/1.0.2.zip'

    depends = ['python2', 'setuptools']


recipe = Pysha3Recipe()
