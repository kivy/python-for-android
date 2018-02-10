import os
try:
    import sh
except ImportError:
    # fallback: emulate the sh API with pbs
    import pbs
    class Sh(object):
        def __getattr__(self, attr):
            return pbs.Command(attr)
    sh = Sh()

from pythonforandroid.recipe import CythonRecipe


class MsgPackRecipe(CythonRecipe):
    version = '0.4.7'
    url = 'https://pypi.python.org/packages/source/m/msgpack-python/msgpack-python-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), "setuptools"]
    call_hostpython_via_targetpython = False

recipe = MsgPackRecipe()
