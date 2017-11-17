from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class CffiRecipe(CompiledComponentsPythonRecipe):
    name = 'cffi'
    version = 'master'
    url = 'git+file:///home/enoch/cffi'

    depends = ['pycparser', 'libffi']

    patches = ['disable-pkg-config.patch']

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None):
        env = super(CffiRecipe, self).get_recipe_env(arch)
        recipe = self.get_recipe('libffi', self.ctx)
        dirs = recipe.get_include_dirs(arch)
        env['CFLAGS'] += ''.join([' -I' + dir for dir in dirs])
        return env


recipe = CffiRecipe()
