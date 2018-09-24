import os
from pythonforandroid.recipe import PythonRecipe


class Secp256k1Recipe(PythonRecipe):

    url = 'https://github.com/ludbb/secp256k1-py/archive/master.zip'

    call_hostpython_via_targetpython = False

    depends = [
        'openssl', ('hostpython2', 'hostpython3crystax'),
        ('python2', 'python3crystax'), 'setuptools',
        'libffi', 'cffi', 'libsecp256k1']

    patches = [
        "cross_compile.patch", "drop_setup_requires.patch",
        "pkg-config.patch", "find_lib.patch", "no-download.patch"]

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(Secp256k1Recipe, self).get_recipe_env(arch, with_flags_in_cc)
        # sets linker to use the correct gcc (cross compiler)
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        libsecp256k1 = self.get_recipe('libsecp256k1', self.ctx)
        libsecp256k1_dir = libsecp256k1.get_build_dir(arch.arch)
        env['LDFLAGS'] += ' -L{}'.format(libsecp256k1_dir)
        env['CFLAGS'] = ' -I' + os.path.join(libsecp256k1_dir, 'include')
        # only keeps major.minor (discards patch)
        python_version = self.ctx.python_recipe.version[0:3]
        # required additional library and path for Crystax
        if self.ctx.ndk == 'crystax':
            ndk_dir_python = os.path.join(self.ctx.ndk_dir, 'sources/python/', python_version)
            env['LDFLAGS'] += ' -L{}'.format(os.path.join(ndk_dir_python, 'libs', arch.arch))
            env['LDFLAGS'] += ' -lpython{}m'.format(python_version)
            # until `pythonforandroid/archs.py` gets merged upstream:
            # https://github.com/kivy/python-for-android/pull/1250/files#diff-569e13021e33ced8b54385f55b49cbe6
            env['CFLAGS'] += ' -I{}/include/python/'.format(ndk_dir_python)
        else:
            env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
            env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python{}'.format(python_version)
            env['LDFLAGS'] += " -lpython{}".format(python_version)
        env['LDFLAGS'] += " -lsecp256k1"
        return env


recipe = Secp256k1Recipe()
