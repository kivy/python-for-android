from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class NetifacesRecipe(CompiledComponentsPythonRecipe):

    version = '0.10.4'

    url = 'https://pypi.python.org/packages/18/fa/dd13d4910aea339c0bb87d2b3838d8fd923c11869b1f6e741dbd0ff3bc00/netifaces-{version}.tar.gz'

    depends = [('python2', 'python3crystax'), 'setuptools']

    site_packages_name = 'netifaces'

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(NetifacesRecipe, self).get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -lpython2.7'
        return env


recipe = NetifacesRecipe()
