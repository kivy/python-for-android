
from pythonforandroid.toolchain import (
    CompiledComponentsPythonRecipe,
    Recipe,
    current_directory,
    info,
    shprint,
)
from os.path import exists, join
import sh
import glob


class PyOpenSSLRecipe(CompiledComponentsPythonRecipe):
    version = '0.13'
    url = 'https://pypi.python.org/packages/source/p/pyOpenSSL/pyOpenSSL-{version}.tar.gz'
    depends = ['openssl', 'python2']

    def prebuild_arch(self, arch):
        super(PyOpenSSLRecipe, self).prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        if exists(join(build_dir, '.patched')):
            print('pyOpenSSL already patched, skipping')
            return
        self.apply_patch('fix-dlfcn.patch', arch.arch)
        shprint(sh.touch, join(build_dir, '.patched'))

    def get_recipe_env(self, arch):
        env = super(PyOpenSSLRecipe, self).get_recipe_env(arch)
        openssl_build_dir = Recipe.get_recipe('openssl', self.ctx).get_build_dir(arch.arch)
        env['CC'] = '%s -I%s' % (env['CC'], join(openssl_build_dir, 'include'))
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch) +
            '-L{}'.format(self.ctx.libs_dir)) + ' -L{}'.format(
            openssl_build_dir)
        return env

recipe = PyOpenSSLRecipe()
