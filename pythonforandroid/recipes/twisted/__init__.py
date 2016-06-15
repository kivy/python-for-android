from pythonforandroid.toolchain import CythonRecipe, shprint, current_directory
from os.path import join
import sh


class TwistedRecipe(CythonRecipe):
    version = '15.5.0'
    url = 'https://pypi.python.org/packages/source/T/Twisted/Twisted-{version}.tar.bz2'

    depends = ['setuptools', 'zope_interface']

    call_hostpython_via_targetpython = False
    install_in_hostpython = True

    def prebuild_arch(self, arch):
        super(TwistedRecipe, self).prebuild_arch(arch)
        # TODO Need to whitelist tty.pyo and termios.so here
        with current_directory(self.get_build_dir(arch.arch)):
            # Remove all tests
            sh.rm('-rf',
                  'twisted/conch/test',
                  'twisted/cred/test',
                  'twisted/names/test',
                  'twisted/mail/test',
                  'twisted/_threads/test',
                  'twisted/internet/test',
                  'twisted/runner/test',
                  'twisted/trial/test',
                  'twisted/trial/_dist/test',
                  'twisted/logger/test',
                  'twisted/test',
                  'twisted/persisted/test',
                  'twisted/words/test',
                  'twisted/web/test',
                  'twisted/pair/test',
                  'twisted/application/test',
                  'twisted/python/test',
                  'twisted/protocols/test',
                  'twisted/manhole/ui/test',
                  'twisted/manhole/test',
                  'twisted/news/test',
                  'twisted/positioning/test',
                  'twisted/scripts/test'
            )

    def get_recipe_env(self, arch):
        env = super(TwistedRecipe, self).get_recipe_env(arch)
        # We add BUILDLIB_PATH to PYTHONPATH so twisted can find _io.so
        env['PYTHONPATH'] = ':'.join([
            self.ctx.get_site_packages_dir(),
            env['BUILDLIB_PATH'],
        ])
        return env


recipe = TwistedRecipe()
