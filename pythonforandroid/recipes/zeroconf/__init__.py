from pythonforandroid.recipe import PythonRecipe
from os.path import join


class ZeroconfRecipe(PythonRecipe):
    name = 'zeroconf'
    version = '0.17.4'
    url = 'https://pypi.python.org/packages/source/z/zeroconf/zeroconf-{version}.tar.gz'
    depends = ['python2', 'netifaces', 'enum34', 'six']

    def get_recipe_env(self, arch=None):
        env = super(ZeroconfRecipe, self).get_recipe_env(arch)

        # TODO: fix hardcoded path
        # This is required to prevent issue with _io.so import.
        hostpython = self.get_recipe('hostpython2', self.ctx)
        env['PYTHONPATH'] = (
            join(hostpython.get_build_dir(arch.arch), 'build',
                 'lib.linux-x86_64-2.7') + ':' + env.get('PYTHONPATH', '')
        )
        return env


recipe = ZeroconfRecipe()
