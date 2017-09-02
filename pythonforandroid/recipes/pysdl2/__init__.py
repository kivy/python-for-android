
from pythonforandroid.toolchain import PythonRecipe, shprint, current_directory, ArchARM
from os.path import exists, join
import sh
import glob

class PySDL2Recipe(PythonRecipe):
    version = '0.9.3'
    url = 'https://bitbucket.org/marcusva/py-sdl2/downloads/PySDL2-{version}.tar.gz'

    depends = ['sdl2']


recipe = PySDL2Recipe()
