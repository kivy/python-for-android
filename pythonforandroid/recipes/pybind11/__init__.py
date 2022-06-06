from pythonforandroid.recipe import PythonRecipe
from os.path import join


class Pybind11Recipe(PythonRecipe):

    version = '2.9.0'
    url = 'https://github.com/pybind/pybind11/archive/refs/tags/v{version}.zip'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False
    install_in_hostpython = True

    def get_include_dir(self, arch):
        return join(self.get_build_dir(arch.arch), 'include')


recipe = Pybind11Recipe()
