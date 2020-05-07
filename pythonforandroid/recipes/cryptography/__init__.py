from pythonforandroid.recipe import CompiledComponentsPythonRecipe, Recipe


class CryptographyRecipe(CompiledComponentsPythonRecipe):
    name = 'cryptography'
    version = '2.8'
    url = 'https://github.com/pyca/cryptography/archive/{version}.tar.gz'
    depends = ['openssl', 'six', 'setuptools', 'cffi']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        openssl_recipe = Recipe.get_recipe('openssl', self.ctx)
        env['CFLAGS'] += openssl_recipe.include_flags(arch)
        env['LDFLAGS'] += openssl_recipe.link_dirs_flags(arch)
        env['LIBS'] = openssl_recipe.link_libs_flags()

        return env


recipe = CryptographyRecipe()
