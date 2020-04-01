from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from multiprocessing import cpu_count
from os.path import join


class NumpyRecipe(CompiledComponentsPythonRecipe):

    version = '1.18.1'
    url = 'https://pypi.python.org/packages/source/n/numpy/numpy-{version}.zip'
    site_packages_name = 'numpy'
    depends = ['setuptools', 'cython']

    patches = [
        join('patches', 'add_libm_explicitly_to_build.patch'),
        join('patches', 'do_not_use_system_libs.patch'),
        join('patches', 'remove_unittest_call.patch'),
        ]

    call_hostpython_via_targetpython = False

    def build_compiled_components(self, arch):
        self.setup_extra_args = ['-j', str(cpu_count())]
        super().build_compiled_components(arch)
        self.setup_extra_args = []

    def rebuild_compiled_components(self, arch, env):
        self.setup_extra_args = ['-j', str(cpu_count())]
        super().rebuild_compiled_components(arch, env)
        self.setup_extra_args = []


recipe = NumpyRecipe()
