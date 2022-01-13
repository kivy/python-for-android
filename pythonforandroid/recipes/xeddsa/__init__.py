from pythonforandroid.recipe import CythonRecipe
from pythonforandroid.toolchain import current_directory, shprint
from os.path import join
import sh


class XedDSARecipe(CythonRecipe):
    name = 'xeddsa'
    version = '0.4.4'
    url = 'https://pypi.python.org/packages/source/X/XEdDSA/XEdDSA-{version}.tar.gz'
    depends = [
        'setuptools',
        'cffi',
        'pynacl',
    ]
    patches = ['remove_dependencies.patch']
    call_hostpython_via_targetpython = False

    def build_arch(self, arch):
        with current_directory(join(self.get_build_dir(arch.arch))):
            env = self.get_recipe_env(arch)
            hostpython = sh.Command(self.ctx.hostpython)
            shprint(
                hostpython, 'ref10/build.py',
                _env=env
            )
            # the library could be `_crypto_sign.cpython-37m-x86_64-linux-gnu.so`
            # or simply `_crypto_sign.so` depending on the platform/distribution
            sh.cp('-a', sh.glob('_crypto_sign*.so'), self.ctx.get_site_packages_dir(arch))
            self.install_python_package(arch)


recipe = XedDSARecipe()
