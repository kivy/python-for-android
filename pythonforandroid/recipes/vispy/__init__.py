
from pythonforandroid.toolchain import PythonRecipe, shprint, current_directory
from os.path import exists, join
import sh
import glob


class VispyRecipe(PythonRecipe):
    version = '0.4.0'
    url = 'https://github.com/vispy/vispy/archive/v{version}.tar.gz'

    depends = ['python2', 'numpy']

    def prebuild_arch(self, arch):
        super(VispyRecipe, self).prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        if exists(join(build_dir, '.patched')):
            print('vispy already patched, skipping')
            return
        self.apply_patch('disable_freetype.patch')
        self.apply_patch('disable_font_triage.patch')
        self.apply_patch('use_es2.patch')
        shprint(sh.touch, join(build_dir, '.patched'))

recipe = VispyRecipe()
