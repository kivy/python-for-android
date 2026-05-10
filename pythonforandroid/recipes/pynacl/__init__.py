from pythonforandroid.recipe import PyProjectRecipe
import os


class PyNaCLRecipe(PyProjectRecipe):
    name = 'pynacl'
    version = '1.3.0'
    url = 'https://github.com/pyca/pynacl/archive/refs/tags/{version}.tar.gz'

    depends = ['hostpython3', 'six', 'setuptools', 'cffi', 'libsodium']
    call_hostpython_via_targetpython = False
    hostpython_prerequisites = ["cffi>=2.0.0"]

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        env['SODIUM_INSTALL'] = 'system'

        libsodium_build_dir = self.get_recipe(
            'libsodium', self.ctx
        ).get_build_dir(arch.arch)

        env['CFLAGS'] += ' -I{}'.format(
            os.path.join(libsodium_build_dir, 'src/libsodium/include')
        )

        for ldflag in [
            self.ctx.get_libs_dir(arch.arch),
            self.ctx.libs_dir,
            libsodium_build_dir
        ]:
            env['LDFLAGS'] += ' -L{}'.format(ldflag)

        return env


recipe = PyNaCLRecipe()
