import os
from pythonforandroid.toolchain import PythonRecipe


class GreenletRecipe(PythonRecipe):
    version = '0.4.9'
    url = 'https://pypi.python.org/packages/source/g/greenlet/greenlet-{version}.tar.gz'
    depends = [('python2', 'python3crystax')]

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(GreenletRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        # sets linker to use the correct gcc (cross compiler)
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        # required additional library and path for Crystax
        if self.ctx.ndk == 'crystax':
            env['LDFLAGS'] += ' -L{}'.format(os.path.join(self.ctx.bootstrap.build_dir, 'libs', arch.arch))
            env['LDFLAGS'] += ' -lpython{}m'.format(self.ctx.python_recipe.version[0:3])
        return env


recipe = GreenletRecipe()
