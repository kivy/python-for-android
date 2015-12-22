
from pythonforandroid.toolchain import Recipe, shprint, current_directory, ArchARM
from pythonforandroid.logger import info
from os.path import exists, join
from os import uname
import glob
import sh

class Python3Recipe(Recipe):
    version = ''
    url = ''
    name = 'python3crystax'

    depends = ['hostpython3']  
    conflicts = ['python2', 'python3']

    def __init__(self, **kwargs):
        super(Python3Recipe, self).__init__(**kwargs)
        self.crystax = lambda *args: True if self.ctx.ndk_is_crystax else False

    def prebuild_arch(self, arch):
        self.ctx.ensure_crystax_python_install_dir()

    def build_arch(self, arch):
        info('doing nothing, the crystax python3 is included in the ndk!')


recipe = Python3Recipe()
