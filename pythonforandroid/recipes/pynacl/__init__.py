from pythonforandroid.recipe import CompiledComponentsPythonRecipe
import os


class PyNaCLRecipe(CompiledComponentsPythonRecipe):
    name = 'pynacl'
    version = '1.3.0'
    url = 'https://pypi.python.org/packages/source/P/PyNaCl/PyNaCl-{version}.tar.gz'

    depends = ['hostpython3', 'six', 'setuptools', 'cffi', 'libsodium']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['SODIUM_INSTALL'] = 'system'

        libsodium_build_dir = self.get_recipe(
            'libsodium', self.ctx).get_build_dir(arch.arch)
        env['CFLAGS'] += ' -I{}'.format(os.path.join(libsodium_build_dir,
                                                     'src/libsodium/include'))
        env['LDFLAGS'] += ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch) +
            '-L{}'.format(self.ctx.libs_dir)) + ' -L{}'.format(
            libsodium_build_dir)

        return env


recipe = PyNaCLRecipe()
