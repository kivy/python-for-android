from pythonforandroid.toolchain import CythonRecipe
from os.path import join


class KiventCoreRecipe(CythonRecipe):
    version = 'master'
    url = 'https://github.com/kivy/kivent/archive/{version}.zip'
    name = 'kivent_core'

    depends = ['kivy']
    
    subbuilddir = False

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        env = super(KiventCoreRecipe, self).get_recipe_env(
            arch, with_flags_in_cc=with_flags_in_cc)
        env['CYTHONPATH'] = self.get_recipe(
            'kivy', self.ctx).get_build_dir(arch.arch)
        return env

    def get_build_dir(self, arch, sub=False):
        builddir = super(KiventCoreRecipe, self).get_build_dir(arch)
        if sub or self.subbuilddir:
            return join(builddir, 'modules', 'core')
        else:
            return builddir
    
    def build_arch(self, arch):
        self.subbuilddir = True
        super(KiventCoreRecipe, self).build_arch(arch)
        self.subbuilddir = False


recipe = KiventCoreRecipe()
