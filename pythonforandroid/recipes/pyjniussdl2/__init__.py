
from pythonforandroid.toolchain import CythonRecipe, shprint, ArchAndroid, current_directory, info
import sh
import glob
from os.path import join, exists


class PyjniusRecipe(CythonRecipe):
    version  = 'master'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.zip'
    depends = ['python2', 'sdl2']
    site_packages_name = 'jnius'

    def prebuild_arch(self, arch):
        super(PyjniusRecipe, self).prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        if exists(join(build_dir, '.patched')):
            print('pyjniussdl2 already pathed, skipping')
            return
        self.apply_patch('sdl2_jnienv_getter.patch')
        shprint(sh.touch, join(build_dir, '.patched'))

    def postbuild_arch(self, arch):
        super(PyjniusRecipe, self).postbuild_arch(arch)
        info('Copying pyjnius java class to classes build dir')
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.cp, '-a', join('jnius', 'src', 'org'), self.ctx.javaclass_dir)


recipe = PyjniusRecipe()
