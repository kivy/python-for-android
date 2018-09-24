import os
from pythonforandroid.recipe import CythonRecipe


class ScryptRecipe(CythonRecipe):

    version = '0.8.6'
    url = 'https://bitbucket.org/mhallin/py-scrypt/get/v{version}.zip'
    depends = [('python2', 'python3crystax'), 'setuptools', 'openssl']
    call_hostpython_via_targetpython = False
    patches = ["remove_librt.patch"]

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        """
        Adds openssl recipe to include and library path.
        """
        env = super(ScryptRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        openssl_build_dir = self.get_recipe(
            'openssl', self.ctx).get_build_dir(arch.arch)
        env['CFLAGS'] += ' -I{}'.format(os.path.join(openssl_build_dir, 'include'))
        env['LDFLAGS'] += ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch) +
            '-L{}'.format(self.ctx.libs_dir)) + ' -L{}'.format(
            openssl_build_dir)
        # required additional library and path for Crystax
        if self.ctx.ndk == 'crystax':
            # only keeps major.minor (discards patch)
            python_version = self.ctx.python_recipe.version[0:3]
            ndk_dir_python = os.path.join(self.ctx.ndk_dir, 'sources/python/', python_version)
            env['LDFLAGS'] += ' -L{}'.format(os.path.join(ndk_dir_python, 'libs', arch.arch))
            env['LDFLAGS'] += ' -lpython{}m'.format(python_version)
            # until `pythonforandroid/archs.py` gets merged upstream:
            # https://github.com/kivy/python-for-android/pull/1250/files#diff-569e13021e33ced8b54385f55b49cbe6
            env['CFLAGS'] += ' -I{}/include/python/'.format(ndk_dir_python)
        return env


recipe = ScryptRecipe()
