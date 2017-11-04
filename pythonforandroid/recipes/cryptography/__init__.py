from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from os.path import dirname, join

class CryptographyRecipe(CompiledComponentsPythonRecipe):
    name = 'cryptography'
    version = 'master'
    url = 'git+file:///home/enoch/cryptography'
    depends = ['idna', 'asn1crypto', 'six', 'cffi', 'enum34', 'ipaddress']

    call_hostpython_via_targetpython = False
    # install_in_hostpython = True

    def get_recipe_env(self, arch):
        env = super(CryptographyRecipe, self).get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -L' + openssl_dir + \
                          ' -lpython2.7'
        return env

recipe = CryptographyRecipe()
