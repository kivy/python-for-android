from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from os.path import dirname, join

class CryptographyRecipe(CompiledComponentsPythonRecipe):
    name = 'cryptography'
    version = '1.3.1'
    url = 'https://pypi.python.org/packages/source/c/cryptography/cryptography-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'cffi', 'enum34', 'openssl', 'ipaddress', 'idna']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(CryptographyRecipe, self).get_recipe_env(arch)
        openssl_dir = self.get_recipe('openssl', self.ctx).get_build_dir(arch.arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7' + \
                         ' -I' + join(openssl_dir, 'include')
        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -L' + openssl_dir + \
                          ' -lpython2.7' + \
                          ' -lssl -lcrypto'
        return env

recipe = CryptographyRecipe()
