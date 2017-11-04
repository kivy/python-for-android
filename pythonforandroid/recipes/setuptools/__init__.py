
from pythonforandroid.toolchain import (
    PythonRecipe,
    Recipe,
    current_directory,
    info,
    shprint,
)
from os.path import join
import sh


class SetuptoolsRecipe(PythonRecipe):
    version = '36.6.0'
    url = 'https://pypi.python.org/packages/45/29/8814bf414e7cd1031e1a3c8a4169218376e284ea2553cc0822a6ea1c2d78/setuptools-36.6.0.zip#md5=74663b15117d9a2cc5295d76011e6fd1'

    depends = ['python2']

    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = SetuptoolsRecipe()
