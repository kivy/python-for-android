
from pythonforandroid.toolchain import CythonRecipe, shprint, ArchAndroid, current_directory, info
import sh
import glob
from os.path import join, exists


class PyjniusRecipe(CythonRecipe):
    version  = 'master'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.zip'
    name = 'pyjnius'
    depends = ['python2', 'sdl']
    site_packages_name = 'jnius'

    def postbuild_arch(self, arch):
        super(PyjniusRecipe, self).postbuild_arch(arch)
        info('Copying pyjnius java class to classes build dir')
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.cp, '-a', join('jnius', 'src', 'org'), self.ctx.javaclass_dir)


recipe = PyjniusRecipe()
