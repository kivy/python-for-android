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
        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        return env

recipe = NetifacesRecipe()
