
from toolchain import PythonRecipe, shprint


class KivyRecipe(PythonRecipe):
    version = 'stable'
    url = 'https://github.com/kivy/kivy/archive/{version}.zip'
    name = 'kivy'

    depends = ['pygame', 'pyjnius', 'android']


recipe = KivyRecipe()
