from pythonforandroid.toolchain import CythonRecipe
from os.path import join


class ScryptRecipe(CythonRecipe):

    url = 'https://bitbucket.org/mhallin/py-scrypt/get/default.zip'

    depends = ['python2', 'setuptools', 'openssl']

    call_hostpython_via_targetpython = False

    patches = ["remove_librt.patch"]

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        """
        Adds openssl recipe to include and library path.
        """
        env = super(ScryptRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        openssl_build_dir = self.get_recipe(
            'openssl', self.ctx).get_build_dir(arch.arch)
        print("openssl_build_dir:", openssl_build_dir)
        env['CC'] = '%s -I%s' % (env['CC'], join(openssl_build_dir, 'include'))
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch) +
            '-L{}'.format(self.ctx.libs_dir)) + ' -L{}'.format(
            openssl_build_dir)
        return env


recipe = ScryptRecipe()
