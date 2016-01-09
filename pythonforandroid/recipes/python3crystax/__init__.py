
from pythonforandroid.recipe import TargetPythonRecipe
from pythonforandroid.toolchain import shprint, current_directory, ArchARM
from pythonforandroid.logger import info
from pythonforandroid.util import ensure_dir
from os.path import exists, join
from os import uname
import glob
import sh

class Python3Recipe(TargetPythonRecipe):
    version = '3.5'
    url = ''
    name = 'python3crystax'

    depends = ['hostpython3crystax']  
    conflicts = ['python2', 'python3']

    from_crystax = True

    def get_dir_name(self):
        name = super(Python3Recipe, self).get_dir_name()
        name += '-version{}'.format(self.version)
        return name

    def build_arch(self, arch):
        info('Extracting CrystaX python3 from NDK package')

        dirn = self.ctx.get_python_install_dir()
        ensure_dir(dirn)

        self.ctx.hostpython = 'python{}'.format(self.version)
        # ensure_dir(join(dirn, 'lib'))
        # ensure_dir(join(dirn, 'lib', 'python{}'.format(self.version),
        #                 'site-packages'))

        # ndk_dir = self.ctx.ndk_dir
        # sh.cp('-r', '/home/asandy/kivytest/crystax_stdlib', join(dirn, 'lib', 'python3.5'))
        # sh.cp('-r', '/home/asandy/android/crystax-ndk-10.3.0/sources/python/3.5/libs/armeabi/modules', join(dirn, 'lib', 'python3.5', 'lib-dynload'))
        # ensure_dir(join(dirn, 'lib', 'site-packages'))

recipe = Python3Recipe()
