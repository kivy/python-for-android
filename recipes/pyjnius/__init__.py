
from toolchain import CythonRecipe, shprint


class PyjniusRecipe(CythonRecipe):
    version  = 'master'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.zip'
    name = 'pyjnius'
    depends = ['python2', 'sdl']


recipe = PyjniusRecipe()
