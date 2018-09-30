from pythonforandroid.recipe import TargetPythonRecipe, Recipe
from pythonforandroid.toolchain import shprint, current_directory, info
from pythonforandroid.patching import (is_darwin, is_api_gt,
                                       check_all, is_api_lt, is_ndk)
from os.path import exists, join, realpath
import sh


class Python3Recipe(TargetPythonRecipe):
    version = 'bpo-30386'
    url = 'https://github.com/inclement/cpython/archive/{version}.zip'
    name = 'python3'

    depends = ['hostpython3']
    conflicts = ['python3crystax', 'python2']
    opt_depends = ['openssl', 'sqlite3']

recipe = Python3Recipe()
