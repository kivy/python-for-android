
from pythonforandroid.toolchain import (
    CompiledComponentsPythonRecipe,
    Recipe,
    current_directory,
    info,
    shprint,
)
from os.path import join
import sh


class PyCryptoRecipe(CompiledComponentsPythonRecipe):
    version = '2.6.1'
    url = 'https://pypi.python.org/packages/source/p/pycrypto/pycrypto-{version}.tar.gz'
    depends = ['openssl', 'python2']
    site_packages_name = 'Crypto'

    patches = ['add_length.patch']

    def get_recipe_env(self, arch=None):
        env = super(PyCryptoRecipe, self).get_recipe_env(arch)
        openssl_build_dir = Recipe.get_recipe('openssl', self.ctx).get_build_dir(arch.arch)
        env['CC'] = '%s -I%s' % (env['CC'], join(openssl_build_dir, 'include'))
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch) +
            '-L{}'.format(self.ctx.libs_dir)) + ' -L{}'.format(
            openssl_build_dir)
        env['EXTRA_CFLAGS'] = '--host linux-armv'
        env['ac_cv_func_malloc_0_nonnull'] = 'yes'
        return env

    def build_compiled_components(self, arch):
        info('Configuring compiled components in {}'.format(self.name))

        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            configure = sh.Command('./configure')
            shprint(configure, '--host=arm-eabi',
                    '--prefix={}'.format(self.ctx.get_python_install_dir()),
                    '--enable-shared', _env=env)
        super(PyCryptoRecipe, self).build_compiled_components(arch)

recipe = PyCryptoRecipe()
