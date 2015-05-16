
from toolchain import CythonRecipe, shprint


class KivyRecipe(CythonRecipe):
    version = 'stable'
    url = 'https://github.com/kivy/kivy/archive/{version}.zip'
    name = 'kivy'

    depends = ['pygame', 'pyjnius', 'android']


recipe = KivyRecipe()
