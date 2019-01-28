from pythonforandroid.recipe import CythonRecipe


class CymunkRecipe(CythonRecipe):
    version = 'master'
    url = 'https://github.com/tito/cymunk/archive/{version}.zip'
    name = 'cymunk'

    depends = [('python2', 'python3crystax', 'python3')]


recipe = CymunkRecipe()
