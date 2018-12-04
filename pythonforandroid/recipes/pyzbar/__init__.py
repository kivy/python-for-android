import os
from pythonforandroid.recipe import PythonRecipe


class PyZBarRecipe(PythonRecipe):

    version = '0.1.7'

    url = 'https://github.com/NaturalHistoryMuseum/pyzbar/archive/v{version}.tar.gz'

    call_hostpython_via_targetpython = False

    depends = [('python2', 'python3'), 'setuptools', 'libzbar']

    # patches = ["zbar-0.10-python-crash.patch"]

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(PyZBarRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        libzbar = self.get_recipe('libzbar', self.ctx)
        libzbar_dir = libzbar.get_build_dir(arch.arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + os.path.join(libzbar_dir, 'include')
        env['LDFLAGS'] += " -landroid -lzbar"
        return env


recipe = PyZBarRecipe()
