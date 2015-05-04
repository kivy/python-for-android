
from toolchain import PythonRecipe


class AndroidRecipe(PythonRecipe):
    name = 'android'
    version = None
    url = None
    depends = ['pygame']


recipe = AndroidRecipe()
