from pythonforandroid.recipe import PythonRecipe


class Pbkdf2Recipe(PythonRecipe):

    # TODO: version
    url = 'https://github.com/dlitz/python-pbkdf2/archive/master.zip'

    depends = ['setuptools']


recipe = Pbkdf2Recipe()
