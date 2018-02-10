from pythonforandroid.toolchain import Bootstrap
from os.path import join, exists
from os import walk
import glob
try:
    import sh
except ImportError:
    # fallback: emulate the sh API with pbs
    import pbs
    class Sh(object):
        def __getattr__(self, attr):
            return pbs.Command(attr)
    sh = Sh()


class EmptyBootstrap(Bootstrap):
    name = 'empty'

    recipe_depends = []

    can_be_chosen_automatically = False

    def run_distribute(self):
        print('empty bootstrap has no distribute')
        exit(1)

bootstrap = EmptyBootstrap()
