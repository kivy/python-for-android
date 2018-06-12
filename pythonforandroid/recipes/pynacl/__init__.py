from pythonforandroid.recipe import CompiledComponentsPythonRecipe

from os.path import join


class PyNACLRecipe(CompiledComponentsPythonRecipe):
    name = 'pynacl'
    version = '1.2.1'
    url = 'https://github.com/pyca/pynacl/archive/{version}.zip'
    depends = ['six', 'setuptools', 'libsodium', 'cffi']
    call_hostpython_via_targetpython = False
    install_in_hostpython = True

    def get_recipe_env(self, arch=None):
        env = super(PyNACLRecipe, self).get_recipe_env(arch)
        libsodium = self.get_recipe('libsodium', self.ctx)
        libsodium_dir = libsodium.get_build_dir(arch.arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] = ' -I'.join([env.get('CFLAGS', '')]) + ' -I' + join(libsodium_dir, 'src/libsodium/include')
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT']
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['LDFLAGS'] = (env.get('CFLAGS', '') + ' -L' +
                          self.ctx.get_libs_dir(arch.arch))
        env['LDFLAGS'] += ' -L{}'.format(join(self.ctx.bootstrap.build_dir, 'libs', arch.arch))
        ndk_dir = self.ctx.ndk_platform
        ndk_lib_dir = join(ndk_dir, 'usr', 'lib')
        env['LDFLAGS'] += ' -L{}'.format(ndk_lib_dir)
        env['LDFLAGS'] += " --sysroot={}".format(self.ctx.ndk_platform)
        env['PYTHONPATH'] = ':'.join([
            self.ctx.get_site_packages_dir(),
            env['BUILDLIB_PATH'],
        ])
        env['PYTHONPATH'] = env['PYTHONPATH'][env['PYTHONPATH'].find(':') + 1:]
        if self.ctx.ndk == 'crystax':
            python_version = self.ctx.python_recipe.version[0:3]
            ndk_dir_python = join(self.ctx.ndk_dir, 'sources/python/', python_version)
            env['LDFLAGS'] += ' -L{}'.format(join(ndk_dir_python, 'libs', arch.arch))
            env['LDFLAGS'] += ' -lpython{}m'.format(python_version)
            env['CFLAGS'] += ' -I{}/include/python/'.format(ndk_dir_python)
        env['SODIUM_INSTALL'] = 'system'
        return env


recipe = PyNACLRecipe()
