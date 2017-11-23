from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class CffiRecipe(CompiledComponentsPythonRecipe):
    name = 'cffi'
    version = '1.11.2'
    url = 'https://pypi.python.org/packages/c9/70/89b68b6600d479034276fed316e14b9107d50a62f5627da37fafe083fde3/cffi-1.11.2.tar.gz#md5=a731487324b501c8295221b629d3f5f3'

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
