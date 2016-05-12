from pythonforandroid.toolchain import CythonRecipe
from os.path import join


class KiventCymunkRecipe(CythonRecipe):
    name = 'kivent_cymunk'

    depends = ['kivent_core', 'cymunk']

    subbuilddir = False

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        env = super(KiventCymunkRecipe, self).get_recipe_env(
            arch, with_flags_in_cc=with_flags_in_cc)
        cymunk = self.get_recipe('cymunk', self.ctx).get_build_dir(arch.arch)
        env['PYTHONPATH'] = join(cymunk, 'cymunk', 'python')
        kivy = self.get_recipe('kivy', self.ctx).get_build_dir(arch.arch)
        kivent = self.get_recipe('kivent_core',
                                 self.ctx).get_build_dir(arch.arch, sub=True)
        env['CYTHONPATH'] = ':'.join((kivy, cymunk, kivent))
        return env

    def prepare_build_dir(self, arch):
        '''No need to prepare, we'll use kivent_core'''
        return

    def get_build_dir(self, arch):
        builddir = self.get_recipe('kivent_core', self.ctx).get_build_dir(arch)
        return join(builddir, 'modules', 'cymunk')


recipe = KiventCymunkRecipe()
