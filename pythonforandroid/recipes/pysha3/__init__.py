import os
from pythonforandroid.recipe import PythonRecipe


# TODO: CompiledComponentsPythonRecipe
class Pysha3Recipe(PythonRecipe):
    version = '1.0.2'
    url = 'https://github.com/tiran/pysha3/archive/{version}.tar.gz'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(Pysha3Recipe, self).get_recipe_env(arch, with_flags_in_cc)
        # CFLAGS may only be used to specify C compiler flags, for macro definitions use CPPFLAGS
        env['CPPFLAGS'] = env['CFLAGS']
        if self.ctx.ndk == 'crystax':
            env['CPPFLAGS'] += ' -I{}/sources/python/{}/include/python/'.format(
                self.ctx.ndk_dir, self.ctx.python_recipe.version[0:3])
        env['CFLAGS'] = ''
        # LDFLAGS may only be used to specify linker flags, for libraries use LIBS
        env['LDFLAGS'] = env['LDFLAGS'].replace('-lm', '').replace('-lcrystax', '')
        env['LDFLAGS'] += ' -L{}'.format(os.path.join(self.ctx.bootstrap.build_dir, 'libs', arch.arch))
        env['LIBS'] = ' -lm'
        if self.ctx.ndk == 'crystax':
            env['LIBS'] += ' -lcrystax -lpython{}m'.format(self.ctx.python_recipe.version[0:3])
        env['LDSHARED'] += env['LIBS']
        return env


recipe = Pysha3Recipe()
