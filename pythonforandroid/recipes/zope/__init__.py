from pythonforandroid.toolchain import PythonRecipe

class ZopeRecipe(PythonRecipe):
    name = 'zope'
    version = '4.1.2'
    url = 'http://pypi.python.org/packages/source/z/zope.interface/zope.interface-{version}.tar.gz'
    depends = ['python2']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(ZopeRecipe, self).get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -lpython2.7'
        return env

recipe = ZopeRecipe()
