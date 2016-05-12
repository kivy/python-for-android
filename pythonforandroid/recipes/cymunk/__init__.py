from pythonforandroid.toolchain import CythonRecipe, shprint, current_directory, ArchARM
from os.path import exists, join
import sh
import glob


class CymunkRecipe(CythonRecipe):
	version = 'master'
	url = 'https://github.com/tito/cymunk/archive/{version}.zip'
	name = 'cymunk'

	depends = [('python2', 'python3')]


recipe = CymunkRecipe()
