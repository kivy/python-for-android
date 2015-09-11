
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
    version = '18.3.1'
    url = 'https://pypi.python.org/packages/source/s/setuptools/setuptools-{version}.tar.gz'

    depends = ['python2']

    def install_python_package(self, name=None, env=None, is_dir=True):
        arch = self.filtered_archs[0]
        if name is None:
            name = self.name
        if env is None:
            env = self.get_recipe_env(arch)

        info('Installing {} into site-packages'.format(self.name))

        with current_directory(self.get_build_dir(arch.arch)):
            # Here we do *not* use the normal hostpython binary in the
            # target python dir, because setuptools tries to import
            # _io.so which would fail.
            hostpython_build_dir = Recipe.get_recipe('hostpython2', self.ctx).get_build_dir('armeabi')
            hostpython_build = sh.Command(join(
                hostpython_build_dir,
                'hostpython'))
	    # build setuptools for android
            shprint(hostpython_build, 'setup.py', 'install', '-O2',
                    '--root={}'.format(self.ctx.get_python_install_dir()),
                    '--install-lib=lib/python2.7/site-packages', _env=env)
	    # build setuptools for python-for-android
            shprint(hostpython_build, 'setup.py', 'install', '-O2',
                    '--root={}'.format(hostpython_build_dir),
                    '--install-lib=Lib/site-packages', _env=env)

recipe = SetuptoolsRecipe()
