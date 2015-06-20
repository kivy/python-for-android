
from toolchain import CythonRecipe, shprint, ensure_dir, current_directory, ArchAndroid, IncludedFilesBehaviour
import sh
from os.path import exists, join


class AndroidRecipe(IncludedFilesBehaviour, CythonRecipe):
    # name = 'android'
    version = None
    url = None
    depends = ['pygame']
    src_filename = 'src'


recipe = AndroidRecipe()
