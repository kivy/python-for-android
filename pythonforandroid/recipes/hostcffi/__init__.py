from pdb import set_trace
from os.path import join
from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory


class HostcffiRecipe(PythonRecipe):
    name = 'cffi'
    version = '1.11.2'
    url = 'https://pypi.python.org/packages/c9/70/89b68b6600d479034276fed316e14b9107d50a62f5627da37fafe083fde3/cffi-1.11.2.tar.gz#md5=a731487324b501c8295221b629d3f5f3'

    depends = ['hostpython2', 'hostpycparser', 'hostcython']

    def get_build_container_dir(self, arch):
        recipe = Recipe.get_recipe('hostpython2', self.ctx)
        return recipe.get_build_container_dir(arch)

    def build_arch(self, arch):
        set_trace()
        with current_directory(self.get_build_dir(arch)):
            self.install_hostpython_package('hostpython2')

    def unpack(self, arch):
        super(HostcffiRecipe, self).unpack('hostpython2')


recipe = HostcffiRecipe()
