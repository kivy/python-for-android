from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.toolchain import current_directory, shprint
import sh


class Psycopg2Recipe(PythonRecipe):
    """
    Requires `libpq-dev` system dependency e.g. for `pg_config` binary.
    If you get `nl_langinfo` symbol runtime error, make sure you're running on
    `ANDROID_API` (`ndk-api`) >= 26, see:
    https://github.com/kivy/python-for-android/issues/1711#issuecomment-465747557
    """
    version = '2.8.4'
    url = 'https://pypi.python.org/packages/source/p/psycopg2/psycopg2-{version}.tar.gz'
    depends = ['libpq', 'setuptools']
    site_packages_name = 'psycopg2'
    call_hostpython_via_targetpython = False

    def prebuild_arch(self, arch):
        libdir = self.ctx.get_libs_dir(arch.arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # pg_config_helper will return the system installed libpq, but we
            # need the one we just cross-compiled
            shprint(sh.sed, '-i',
                    "s|pg_config_helper.query(.libdir.)|'{}'|".format(libdir),
                    'setup.py')

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['LDFLAGS'] = "{} -L{}".format(env['LDFLAGS'], self.ctx.get_libs_dir(arch.arch))
        env['EXTRA_CFLAGS'] = "--host linux-armv"
        return env

    def install_python_package(self, arch, name=None, env=None, is_dir=True):
        '''Automate the installation of a Python package (or a cython
        package where the cython components are pre-built).'''
        if env is None:
            env = self.get_recipe_env(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)

            shprint(hostpython, 'setup.py', 'build_ext', '--static-libpq',
                    _env=env)
            shprint(hostpython, 'setup.py', 'install', '-O2',
                    '--root={}'.format(self.ctx.get_python_install_dir()),
                    '--install-lib=.', _env=env)


recipe = Psycopg2Recipe()
