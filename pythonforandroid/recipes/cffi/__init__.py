import os
from pythonforandroid.recipe import PyProjectRecipe


class CffiRecipe(PyProjectRecipe):
    """
    Extra system dependencies: autoconf, automake and libtool.
    """
    name = 'cffi'
    version = '2.0.0'
    url = 'https://github.com/python-cffi/cffi/archive/refs/tags/v{version}.tar.gz'

    depends = ['pycparser', 'libffi']

    patches = ['disable-pkg-config.patch']

    def get_hostrecipe_env(self, arch=None):
        # fixes missing ffi.h on some host systems (e.g. gentoo)
        env = super().get_hostrecipe_env(arch)
        libffi = self.get_recipe('libffi', self.ctx)
        includes = libffi.get_include_dirs(arch)
        env['FFI_INC'] = ",".join(includes)
        return env

    def get_recipe_env(self, arch=None, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        libffi = self.get_recipe('libffi', self.ctx)
        includes = libffi.get_include_dirs(arch)
        env['CFLAGS'] = ' -I'.join([env.get('CFLAGS', '')] + includes)
        env['CFLAGS'] += ' -I{}'.format(self.ctx.python_recipe.include_root(arch.arch))
        env['LDFLAGS'] = (env.get('CFLAGS', '') + ' -L' +
                          self.ctx.get_libs_dir(arch.arch))
        env['LDFLAGS'] += ' -L{}'.format(os.path.join(self.ctx.bootstrap.build_dir, 'libs', arch.arch))
        # required for libc and libdl
        env['LDFLAGS'] += ' -L{}'.format(arch.ndk_lib_dir_versioned)
        env['LDFLAGS'] += ' -L{}'.format(self.ctx.python_recipe.link_root(arch.arch))
        env['LDFLAGS'] += ' -lpython{}'.format(self.ctx.python_recipe.link_version)
        return env


recipe = CffiRecipe()
