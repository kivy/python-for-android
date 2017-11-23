
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
    version = '37.0.0'
    url = 'https://pypi.python.org/packages/7c/cb/bdfbb0b6a56459d5461768de824d4f40ec4c4c778f3a8fb0b84c25f03b68/setuptools-37.0.0.zip#md5=f905ca70d2db37b7284c0f6314ab6814'

    depends = ['python2']

    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = SetuptoolsRecipe()
