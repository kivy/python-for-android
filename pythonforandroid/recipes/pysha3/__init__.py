import os
from pythonforandroid.recipe import PythonRecipe


# TODO: CompiledComponentsPythonRecipe
class Pysha3Recipe(PythonRecipe):
    version = '1.0.2'
    url = 'https://github.com/tiran/pysha3/archive/{version}.tar.gz'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        # CFLAGS may only be used to specify C compiler flags, for macro definitions use CPPFLAGS
        env['CPPFLAGS'] = env['CFLAGS']
        env['CFLAGS'] = ''
        # LDFLAGS may only be used to specify linker flags, for libraries use LIBS
        env['LDFLAGS'] = env['LDFLAGS'].replace('-lm', '')
        env['LDFLAGS'] += ' -L{}'.format(os.path.join(self.ctx.bootstrap.build_dir, 'libs', arch.arch))
        env['LIBS'] = ' -lm'
        env['LDSHARED'] += env['LIBS']
        return env


recipe = Pysha3Recipe()
