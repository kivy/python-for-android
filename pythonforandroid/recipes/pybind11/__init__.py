from pythonforandroid.recipe import Recipe
from os.path import join


class Pybind11Recipe(Recipe):

    version = '2.9.0'
    url = 'https://github.com/pybind/pybind11/archive/refs/tags/v{version}.zip'

    def get_include_dir(self, arch):
        return join(self.get_build_dir(arch.arch), 'include')


recipe = Pybind11Recipe()
