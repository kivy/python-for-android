from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class CryptographyRecipe(CompiledComponentsPythonRecipe):
    name = 'cryptography'
    version = '1.3'
    url = 'https://github.com/pyca/cryptography/archive/{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'openssl', 'idna', 'pyasn1', 'six', 'setuptools', 'enum34', 'ipaddress', 'cffi']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(CryptographyRecipe, self).get_recipe_env(arch)
        r = self.get_recipe('openssl', self.ctx)
        openssl_dir = r.get_build_dir(arch.arch)
        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['LDFLAGS'] += ' -L' + openssl_dir + \
                          ' -lssl' + r.version + \
                          ' -lcrypto' + r.version
        return env


recipe = CryptographyRecipe()
