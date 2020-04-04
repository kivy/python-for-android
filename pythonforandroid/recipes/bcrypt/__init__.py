from pythonforandroid.recipe import CompiledComponentsPythonRecipe, Recipe


class BCryptRecipe(CompiledComponentsPythonRecipe):
    name = 'bcrypt'
    version = '3.1.7'
    url = 'https://github.com/pyca/bcrypt/archive/{version}.tar.gz'
    depends = ['openssl', 'cffi']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        openssl_recipe = Recipe.get_recipe('openssl', self.ctx)
        env['CFLAGS'] += openssl_recipe.include_flags(arch)
        env['LDFLAGS'] += openssl_recipe.link_dirs_flags(arch)
        env['LIBS'] = openssl_recipe.link_libs_flags()

        return env


recipe = BCryptRecipe()
