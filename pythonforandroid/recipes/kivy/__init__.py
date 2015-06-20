
from toolchain import CythonRecipe, shprint, current_directory, ArchAndroid
from os.path import exists, join
import sh
import glob


class KivyRecipe(CythonRecipe):
    version = 'stable'
    url = 'https://github.com/kivy/kivy/archive/{version}.zip'
    name = 'kivy'

    depends = ['pygame', 'pyjnius', 'android']


recipe = KivyRecipe()
