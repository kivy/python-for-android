from pythonforandroid.recipe import CompiledComponentsPythonRecipe

class NetifacesRecipe(CompiledComponentsPythonRecipe):
    name = 'netifaces'
    version = '0.10.4'
    url = 'https://pypi.python.org/packages/source/n/netifaces/netifaces-{version}.tar.gz'
    depends = ['python2', 'setuptools']
    call_hostpython_via_targetpython = False
    site_packages_name = 'netifaces'

    def get_recipe_env(self, arch=None):
        env = super(NetifacesRecipe, self).get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -lpython2.7'
        return env

recipe = NetifacesRecipe()
