from pdb import set_trace
from os.path import join
from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory


class HostcythonRecipe(PythonRecipe):
    name = 'cython'
    version = '0.27.3'
    url = 'https://pypi.python.org/packages/ee/2a/c4d2cdd19c84c32d978d18e9355d1ba9982a383de87d0fcb5928553d37f4/Cython-0.27.3.tar.gz#md5=6149238287d662bd5d5e572482252493'

    depends = ['hostpython2']

    def get_build_container_dir(self, arch):
        recipe = Recipe.get_recipe('hostpython2', self.ctx)
        return recipe.get_build_container_dir(arch)

    def build_arch(self, arch):
        set_trace()
        with current_directory(self.get_build_dir(arch)):
            self.install_hostpython_package('hostpython2')

    def unpack(self, arch):
        super(HostcythonRecipe, self).unpack('hostpython2')


recipe = HostcythonRecipe()
