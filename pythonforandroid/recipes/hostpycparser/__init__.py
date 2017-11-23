from pdb import set_trace
from os.path import join
from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory


class HostpycparserRecipe(PythonRecipe):
    name = 'pycparser'
    version = '2.18'
    url = 'https://pypi.python.org/packages/8c/2d/aad7f16146f4197a11f8e91fb81df177adcc2073d36a17b1491fd09df6ed/pycparser-2.18.tar.gz#md5=72370da54358202a60130e223d488136'

    depends = ['hostpython2']

    def get_build_container_dir(self, arch):
        recipe = Recipe.get_recipe('hostpython2', self.ctx)
        return recipe.get_build_container_dir(arch)

    def build_arch(self, arch):
        set_trace()
        with current_directory(self.get_build_dir(arch)):
            self.install_hostpython_package('hostpython2')

    def unpack(self, arch):
        super(HostpycparserRecipe, self).unpack('hostpython2')


recipe = HostpycparserRecipe()
