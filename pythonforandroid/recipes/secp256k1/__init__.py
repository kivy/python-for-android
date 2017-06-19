from os.path import join
from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class Secp256k1Recipe(CompiledComponentsPythonRecipe):

    url = 'https://github.com/ludbb/secp256k1-py/archive/master.zip'

    call_hostpython_via_targetpython = False

    depends = [
        'openssl', 'hostpython2', 'python2', 'setuptools',
        'libffi', 'cffi', 'libsecp256k1']

    patches = ["cross_compile.patch", "pkg-config.patch", "find_lib.patch"]

    def get_recipe_env(self, arch=None):
        env = super(Secp256k1Recipe, self).get_recipe_env(arch)
        libsecp256k1 = self.get_recipe('libsecp256k1', self.ctx)
        libsecp256k1_dir = libsecp256k1.get_build_dir(arch.arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] = ' -I' + join(libsecp256k1_dir, 'include')
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        env['LDSHARED'] = env['CC'] + \
            ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['LDFLAGS'] += ' -L{}'.format(libsecp256k1_dir)
        # TODO: hardcoded Python version
        env['LDFLAGS'] += " -landroid -lpython2.7 -lsecp256k1"
        return env


recipe = Secp256k1Recipe()
