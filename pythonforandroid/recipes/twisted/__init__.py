
import glob
from pythonforandroid.toolchain import (
    CythonRecipe,
    Recipe,
    current_directory,
    info,
    shprint,
)
from os.path import join
import sh


class TwistedRecipe(CythonRecipe):
    version = '15.4.0'
    url = 'https://pypi.python.org/packages/source/T/Twisted/Twisted-{version}.tar.bz2'

    depends = ['setuptools', 'zope_interface']

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

    def install_python_package(self, name=None, env=None, is_dir=True):
        arch = self.filtered_archs[0]
        if name is None:
            name = self.name
        if env is None:
            env = self.get_recipe_env(arch)

        info('Installing {} into site-packages'.format(self.name))

        with current_directory(self.get_build_dir(arch.arch)):
            # Here we do *not* use the normal hostpython binary in the
            # target python dir, because twisted tries to import
            # _io.so which would fail.
            hostpython_build = sh.Command(join(
                Recipe.get_recipe('hostpython2', self.ctx).get_build_dir('armeabi'),
                'hostpython'))
            shprint(hostpython_build, 'setup.py', 'install', '-O2',
                    '--root={}'.format(self.ctx.get_python_install_dir()),
                    '--install-lib=lib/python2.7/site-packages', _env=env)

recipe = TwistedRecipe()
