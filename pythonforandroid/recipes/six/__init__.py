from pythonforandroid.toolchain import PythonRecipe

class SixRecipe(PythonRecipe):
    version = '1.9.0'
    url = 'https://pypi.python.org/packages/source/s/six/six-{version}.tar.gz'
    depends = [('python2', 'python3crystax')]
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super(SixRecipe, self).get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -lpython2.7'
        return env

recipe = SixRecipe()
