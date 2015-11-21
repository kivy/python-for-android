
from pythonforandroid.toolchain import (
    PythonRecipe,
    Recipe,
    current_directory,
    info,
    shprint,
)
from os.path import join
import sh


class HostCythonRecipe(PythonRecipe):
    version = '0.23.4'
    url = 'https://pypi.python.org/packages/source/C/Cython/Cython-{version}.tar.gz'
    depends = ['python2']
    call_hostpython_via_targetpython = False
    install_in_hostpython = True
    install_in_targetpython = False

    def get_recipe_env(self, arch=None):
        env = super(HostCythonRecipe, self).get_recipe_env(arch)
        from pprint import pprint
        pprint(env)
        cenv = {
            "PATH": env["PATH"],
            "BUILDLIB_PATH": env["BUILDLIB_PATH"]
        }
        return cenv

recipe = HostCythonRecipe()
