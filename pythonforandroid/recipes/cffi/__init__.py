from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class CffiRecipe(CompiledComponentsPythonRecipe):
    name = 'cffi'
    version = 'local'
    url = 'git+file:///home/enoch/cffi'

    depends = [('python2', 'python3crystax'), 'setuptools', 'pycparser', 'libffi']

    patches = ['disable-pkg-config.patch']

    call_hostpython_via_targetpython = False
    # install_in_hostpython = True

    def get_recipe_env(self, arch=None):
        env = super(CffiRecipe, self).get_recipe_env(arch)
        libffi = self.get_recipe('libffi', self.ctx)
        includes = libffi.get_include_dirs(arch)
        env['CFLAGS'] += ''.join([' -I' + inc for inc in includes])
        return env


recipe = CffiRecipe()
