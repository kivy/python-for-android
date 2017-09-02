import os
import sh
from pythonforandroid.recipe import CythonRecipe


class MsgPackRecipe(CythonRecipe):
    version = '0.4.7'
    url = 'https://pypi.python.org/packages/source/m/msgpack-python/msgpack-python-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), "setuptools"]
    call_hostpython_via_targetpython = False

recipe = MsgPackRecipe()
