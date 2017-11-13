import os
import sh
from pythonforandroid.recipe import CythonRecipe


class WSAccellRecipe(CythonRecipe):
    version = '0.6.2'
    url = 'https://pypi.python.org/packages/source/w/wsaccel/wsaccel-{version}.tar.gz'
    depends = [('python2', 'python3crystax')]
    call_hostpython_via_targetpython = False

recipe = WSAccellRecipe()
