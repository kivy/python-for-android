import os
from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class CffiRecipe(CompiledComponentsPythonRecipe):
    """
    Extra system dependencies: autoconf, automake and libtool.
    """
    name = 'cffi'
    version = '1.13.2'
    url = 'https://pypi.python.org/packages/source/c/cffi/cffi-{version}.tar.gz'

    depends = ['setuptools', 'pycparser', 'libffi']

    patches = ['disable-pkg-config.patch']

    # call_hostpython_via_targetpython = False
    install_in_hostpython = True

    def get_hostrecipe_env(self, arch=None):
        # fixes missing ffi.h on some host systems (e.g. gentoo)
        env = super().get_hostrecipe_env(arch)
        libffi = self.get_recipe('libffi', self.ctx)
        includes = libffi.get_include_dirs(arch)
        env['FFI_INC'] = ",".join(includes)
        return env

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)
        libffi = self.get_recipe('libffi', self.ctx)
        includes = libffi.get_include_dirs(arch)
        env['CFLAGS'] = ' -I'.join([env.get('CFLAGS', '')] + includes)
        env['CFLAGS'] += ' -I{}'.format(self.ctx.python_recipe.include_root(arch.arch))
        env['LDFLAGS'] = (env.get('CFLAGS', '') + ' -L' +
                          self.ctx.get_libs_dir(arch.arch))
        env['LDFLAGS'] += ' -L{}'.format(os.path.join(self.ctx.bootstrap.build_dir, 'libs', arch.arch))
        # required for libc and libdl
        ndk_dir = self.ctx.ndk_platform
        ndk_lib_dir = os.path.join(ndk_dir, 'usr', 'lib')
        env['LDFLAGS'] += ' -L{}'.format(ndk_lib_dir)
        env['PYTHONPATH'] = ':'.join([
            self.ctx.get_site_packages_dir(),
            env['BUILDLIB_PATH'],
        ])
        env['LDFLAGS'] += ' -L{}'.format(self.ctx.python_recipe.link_root(arch.arch))
        env['LDFLAGS'] += ' -lpython{}'.format(self.ctx.python_recipe.major_minor_version_string)
        if 'python3' in self.ctx.python_recipe.name:
            env['LDFLAGS'] += 'm'
        return env


recipe = CffiRecipe()
