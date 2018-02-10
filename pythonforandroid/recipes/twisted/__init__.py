
import glob
from pythonforandroid.toolchain import (
    CythonRecipe,
    Recipe,
    current_directory,
    info,
    shprint,
)
from os.path import join
try:
    import sh
except ImportError:
    # fallback: emulate the sh API with pbs
    import pbs
    class Sh(object):
        def __getattr__(self, attr):
            return pbs.Command(attr)
    sh = Sh()


class TwistedRecipe(CythonRecipe):
    version = '17.9.0'
    url = 'https://github.com/twisted/twisted/archive/twisted-{version}.tar.gz'

    depends = ['setuptools', 'zope_interface', 'incremental', 'constantly']

    call_hostpython_via_targetpython = False
    install_in_hostpython = True

    def prebuild_arch(self, arch):
        super(TwistedRecipe, self).prebuild_arch(arch)
        # TODO Need to whitelist tty.pyo and termios.so here
        print('Should remove twisted tests etc. here, but skipping for now')

    def get_recipe_env(self, arch):
        env = super(TwistedRecipe, self).get_recipe_env(arch)
        # We add BUILDLIB_PATH to PYTHONPATH so twisted can find _io.so
        env['PYTHONPATH'] = ':'.join([
            self.ctx.get_site_packages_dir(),
            env['BUILDLIB_PATH'],
        ])
        return env

recipe = TwistedRecipe()
