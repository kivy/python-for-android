from pythonforandroid.recipe import CompiledComponentsPythonRecipe, Recipe


class CryptographyRecipe(CompiledComponentsPythonRecipe):
    name = 'cryptography'
    version = '2.3.1'
    url = 'https://github.com/pyca/cryptography/archive/{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'openssl', 'idna', 'asn1crypto',
               'six', 'setuptools', 'enum34', 'ipaddress', 'cffi']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(CryptographyRecipe, self).get_recipe_env(arch)

        openssl_recipe = Recipe.get_recipe('openssl', self.ctx)
        env['CFLAGS'] += openssl_recipe.include_flags(arch)
        env['LDFLAGS'] += openssl_recipe.link_flags(arch)

        return env


recipe = CryptographyRecipe()
