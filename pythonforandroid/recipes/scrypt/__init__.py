from pythonforandroid.recipe import CythonRecipe


class ScryptRecipe(CythonRecipe):

    version = '0.8.6'
    url = 'https://bitbucket.org/mhallin/py-scrypt/get/v{version}.zip'
    depends = [('python2', 'python3', 'python3crystax'),
               'setuptools', 'openssl']
    call_hostpython_via_targetpython = False
    patches = ["remove_librt.patch"]

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        """
        Adds openssl recipe to include and library path.
        """
        env = super(ScryptRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        openssl_recipe = self.get_recipe('openssl', self.ctx)
        env['CFLAGS'] += openssl_recipe.include_flags(arch)
        env['LDFLAGS'] += ' -L{}'.format(self.ctx.get_libs_dir(arch.arch)) + \
                          ' -L{}'.format(self.ctx.libs_dir) + \
                          openssl_recipe.link_flags(arch)
        return env


recipe = ScryptRecipe()
