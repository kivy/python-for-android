from pythonforandroid.recipe import CompiledComponentsPythonRecipe, Recipe
from pythonforandroid.toolchain import (
    current_directory,
    info,
    shprint,
)
import sh


class PyCryptoRecipe(CompiledComponentsPythonRecipe):
    version = '2.7a1'
    url = 'https://github.com/dlitz/pycrypto/archive/v{version}.zip'
    depends = ['openssl', 'python3']
    site_packages_name = 'Crypto'
    call_hostpython_via_targetpython = False
    patches = ['add_length.patch']

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)
        openssl_recipe = Recipe.get_recipe('openssl', self.ctx)
        env['CC'] = env['CC'] + openssl_recipe.include_flags(arch)

        env['LDFLAGS'] += ' -L{}'.format(self.ctx.get_libs_dir(arch.arch))
        env['LDFLAGS'] += ' -L{}'.format(self.ctx.libs_dir)
        env['LDFLAGS'] += openssl_recipe.link_dirs_flags(arch)
        env['LIBS'] = env.get('LIBS', '') + openssl_recipe.link_libs_flags()

        env['EXTRA_CFLAGS'] = '--host linux-armv'
        env['ac_cv_func_malloc_0_nonnull'] = 'yes'
        return env

    def build_compiled_components(self, arch):
        info('Configuring compiled components in {}'.format(self.name))

        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            configure = sh.Command('./configure')
            shprint(configure, '--host=arm-eabi',
                    '--prefix={}'.format(self.ctx.get_python_install_dir(arch.arch)),
                    '--enable-shared', _env=env)
        super().build_compiled_components(arch)


recipe = PyCryptoRecipe()
