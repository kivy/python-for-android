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
            python_version = self.ctx.python_recipe.version[0:3]
            site_packages_dir = 'lib/python{python_version}/site-packages'.format(
                python_version=python_version)
            site_packages = join(self.ctx.get_python_install_dir(),
                                 site_packages_dir)
            shprint(sh.cp, '_crypto_sign.so', site_packages)
            self.install_python_package(arch)


recipe = XedDSARecipe()
