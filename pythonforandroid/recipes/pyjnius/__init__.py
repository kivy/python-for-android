from pythonforandroid.recipe import CythonRecipe
from pythonforandroid.toolchain import shprint, current_directory, info
from pythonforandroid.patching import will_build
import sh
from os.path import join


class PyjniusRecipe(CythonRecipe):
    version = '1.1.3'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.zip'
    name = 'pyjnius'
    depends = [('python2', 'python3', 'python3crystax'), ('genericndkbuild', 'sdl2', 'sdl'), 'six']
    site_packages_name = 'jnius'

    patches = [('sdl2_jnienv_getter.patch', will_build('sdl2')),
               ('genericndkbuild_jnienv_getter.patch', will_build('genericndkbuild'))]

    def postbuild_arch(self, arch):
        super(PyjniusRecipe, self).postbuild_arch(arch)
        info('Copying pyjnius java class to classes build dir')
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.cp, '-a', join('jnius', 'src', 'org'), self.ctx.javaclass_dir)


recipe = PyjniusRecipe()
