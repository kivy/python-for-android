
from pythonforandroid.toolchain import CythonRecipe, shprint, ensure_dir, current_directory, ArchAndroid, IncludedFilesBehaviour
import sh
from os.path import exists, join


class AndroidRecipe(IncludedFilesBehaviour, CythonRecipe):
    # name = 'android'
    version = None
    url = None

    src_filename = 'src'

    depends = ['pygame']
    conflicts = ['sdl2']


recipe = AndroidRecipe()
