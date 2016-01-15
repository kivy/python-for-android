from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from os.path import join


class NetifacesRecipe(CompiledComponentsPythonRecipe):
    name = 'netifaces'
    version = '0.10.4'
    url = 'https://pypi.python.org/packages/source/n/netifaces/netifaces-{version}.tar.gz'
    site_packages_name = 'netifaces'
    depends = ['python2', 'setuptools']

    def get_recipe_env(self, arch=None):
        env = super(NetifacesRecipe, self).get_recipe_env(arch)

        # TODO: fix hardcoded path
        # This is required to prevent issue with _io.so import.
        hostpython = self.get_recipe('hostpython2', self.ctx)
        env['PYTHONPATH'] = (
            join(hostpython.get_build_dir(arch.arch), 'build',
                 'lib.linux-x86_64-2.7') + ':' + env.get('PYTHONPATH', '')
        )
        return env


recipe = NetifacesRecipe()
