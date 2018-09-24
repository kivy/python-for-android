from pythonforandroid.recipe import PythonRecipe


class PycryptodomeRecipe(PythonRecipe):
    version = '3.4.6'
    url = 'https://github.com/Legrandin/pycryptodome/archive/v{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools', 'cffi']

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(PycryptodomeRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        # sets linker to use the correct gcc (cross compiler)
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        return env


recipe = PycryptodomeRecipe()
