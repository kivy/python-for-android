from pythonforandroid.toolchain import PythonRecipe

class PyASN1Recipe(PythonRecipe):
    version = '0.1.8'
    url = 'https://pypi.python.org/packages/source/p/pyasn1/pyasn1-{version}.tar.gz'
    depends = ['python2']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(PyASN1Recipe, self).get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -lpython2.7'
        return env

recipe = PyASN1Recipe()
