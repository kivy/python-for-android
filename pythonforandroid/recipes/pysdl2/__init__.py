
from pythonforandroid.toolchain import PythonRecipe, shprint, current_directory, ArchARM
from os.path import exists, join
try:
    import sh
except ImportError:
    # fallback: emulate the sh API with pbs
    import pbs
    class Sh(object):
        def __getattr__(self, attr):
            return pbs.Command(attr)
    sh = Sh()

import glob

class PySDL2Recipe(PythonRecipe):
    version = '0.9.3'
    url = 'https://bitbucket.org/marcusva/py-sdl2/downloads/PySDL2-{version}.tar.gz'

    depends = ['sdl2']


recipe = PySDL2Recipe()
