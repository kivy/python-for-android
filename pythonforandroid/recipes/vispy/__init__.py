
from pythonforandroid.toolchain import PythonRecipe, shprint, current_directory
from os.path import exists, join
import sh
import glob


class VispyRecipe(PythonRecipe):
    version = 'master'
    url = 'https://github.com/vispy/vispy/archive/{version}.zip'

    depends = ['python2', 'numpy']

recipe = VispyRecipe()
