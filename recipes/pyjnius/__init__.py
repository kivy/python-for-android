
from toolchain import PythonRecipe, shprint


class PyjniusRecipe(PythonRecipe):
    version  = 'master'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.zip'
    name = 'pyjnius'
    depends = ['python2', 'sdl']


recipe = PyjniusRecipe()
