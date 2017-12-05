from pythonforandroid.toolchain import CompiledComponentsPythonRecipe, shprint, shutil, current_directory
from os.path import join, exists
import sh

class PyLevelDBRecipe(CompiledComponentsPythonRecipe):
    version = '0.193'
    url = 'https://pypi.python.org/packages/source/l/leveldb/leveldb-{version}.tar.gz'
    depends = ['snappy', 'leveldb', 'hostpython2', 'python2', 'setuptools']
    patches = ['bindings-only.patch']
    call_hostpython_via_targetpython = False # Due to setuptools
    site_packages_name = 'leveldb'

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # Remove source in this pypi package
            sh.rm('-rf', 'leveldb', 'leveldb.egg-info', 'snappy')
            # Use source from leveldb recipe
            sh.ln('-s', self.get_recipe('leveldb', self.ctx).get_build_dir(arch.arch), 'leveldb')
        # Build and install python bindings
        super(PyLevelDBRecipe, self).build_arch(arch)

    def get_recipe_env(self, arch):
        env = super(PyLevelDBRecipe, self).get_recipe_env(arch)
        # Copy environment from leveldb recipe
        env.update(self.get_recipe('leveldb', self.ctx).get_recipe_env(arch))
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['LDFLAGS'] += ' -lpython2.7' + \
                          ' -lleveldb'
        return env

recipe = PyLevelDBRecipe()
