from pythonforandroid.toolchain import CythonRecipe
from os.path import join


class KiventParticlesRecipe(CythonRecipe):
    name = 'kivent_particles'

    depends = ['kivent_core']

    subbuilddir = False

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        env = super(KiventParticlesRecipe, self).get_recipe_env(
            arch, with_flags_in_cc=with_flags_in_cc)
        kivy = self.get_recipe('kivy', self.ctx).get_build_dir(arch.arch)
        kivent = self.get_recipe('kivent_core',
                                 self.ctx).get_build_dir(arch.arch, sub=True)
        env['CYTHONPATH'] = ':'.join((kivy, kivent))
        return env

    def prepare_build_dir(self, arch):
        '''No need to prepare, we'll use kivent_core'''
        return

    def get_build_dir(self, arch):
        builddir = self.get_recipe('kivent_core', self.ctx).get_build_dir(arch)
        return join(builddir, 'modules', 'particles')


recipe = KiventParticlesRecipe()
