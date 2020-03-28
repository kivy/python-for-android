from os.path import join
from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class PymunkRecipe(CompiledComponentsPythonRecipe):
    name = "pymunk"
    version = '5.5.0'
    url = 'https://pypi.python.org/packages/source/p/pymunk/pymunk-{version}.zip'
    depends = ['cffi', 'setuptools']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['LDFLAGS'] += " -shared -llog"
        env['LDFLAGS'] += ' -L{}'.format(join(self.ctx.ndk_platform, 'usr', 'lib'))
        env['LIBS'] = env.get('LIBS', '') + ' -landroid'
        return env


recipe = PymunkRecipe()
