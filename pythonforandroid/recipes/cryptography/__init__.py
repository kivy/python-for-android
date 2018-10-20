from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from os.path import join


class CryptographyRecipe(CompiledComponentsPythonRecipe):
    name = 'cryptography'
    version = '2.3.1'
    url = 'https://github.com/pyca/cryptography/archive/{version}.tar.gz'

    # install requires
    #   * six
    #   * cffi
    #   * idna
    #   * asn1crypto
    # py 2 additional install requires, define manually if you want to install in python 2
    #   * enum34
    #   * ipaddress
    depends = [('python2', 'python3crystax'), 'openssl', 'setuptools', 'six', 'cffi', 'idna', 'asn1crypto']

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(CryptographyRecipe, self).get_recipe_env(arch)
        r = self.get_recipe('openssl', self.ctx)
        openssl_dir = r.get_build_dir(arch.arch)
        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['CFLAGS'] += ' -I' + join(openssl_dir, 'include')
        env['LDFLAGS'] += ' -L' + openssl_dir + \
                          ' -lssl' + r.version + \
                          ' -lcrypto' + r.version
        return env


recipe = CryptographyRecipe()
