import sh

from multiprocessing import cpu_count
from os.path import exists, join, isfile

from pythonforandroid.logger import shprint
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import (
    BuildInterruptingException,
    current_directory,
    ensure_dir,
)


class Hostpython3Recipe(Recipe):
    '''
    The hostpython3's recipe.

    .. versionchanged:: 2019.10.06.post0
        Refactored from deleted class ``python.HostPythonRecipe`` into here.

    .. versionchanged:: 0.6.0
        Refactored into  the new class
        :class:`~pythonforandroid.python.HostPythonRecipe`
    '''

    version = '3.8.1'
    name = 'hostpython3'

    build_subdir = 'native-build'
    '''Specify the sub build directory for the hostpython3 recipe. Defaults
    to ``native-build``.'''

    url = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'
    '''The default url to download our host python recipe. This url will
    change depending on the python version set in attribute :attr:`version`.'''

    @property
    def _exe_name(self):
        '''
        Returns the name of the python executable depending on the version.
        '''
        if not self.version:
            raise BuildInterruptingException(
                'The hostpython recipe must have set version'
            )
        version = self.version.split('.')[0]
        return 'python{major_version}'.format(major_version=version)

    @property
    def python_exe(self):
        '''Returns the full path of the hostpython executable.'''
        return join(self.get_path_to_python(), self._exe_name)

    def should_build(self, arch):
        if exists(self.python_exe):
            # no need to build, but we must set hostpython for our Context
            self.ctx.hostpython = self.python_exe
            return False
        return True

    def get_build_container_dir(self, arch=None):
        choices = self.check_recipe_choices()
        dir_name = '-'.join([self.name] + choices)
        return join(self.ctx.build_dir, 'other_builds', dir_name, 'desktop')

    def get_build_dir(self, arch=None):
        '''
        .. note:: Unlike other recipes, the hostpython build dir doesn't
            depend on the target arch
        '''
        return join(self.get_build_container_dir(), self.name)

    def get_path_to_python(self):
        return join(self.get_build_dir(), self.build_subdir)

    def build_arch(self, arch):
        recipe_build_dir = self.get_build_dir(arch.arch)

        # Create a subdirectory to actually perform the build
        build_dir = join(recipe_build_dir, self.build_subdir)
        ensure_dir(build_dir)

        with current_directory(recipe_build_dir):
            # Configure the build
            with current_directory(build_dir):
                if not exists('config.status'):
                    shprint(sh.Command(join(recipe_build_dir, 'configure')))

            # Create the Setup file. This copying from Setup.dist is
            # the normal and expected procedure before Python 3.8, but
            # after this the file with default options is already named "Setup"
            setup_dist_location = join('Modules', 'Setup.dist')
            if exists(setup_dist_location):
                shprint(sh.cp, setup_dist_location,
                        join(build_dir, 'Modules', 'Setup'))
            else:
                # Check the expected file does exist
                setup_location = join('Modules', 'Setup')
                if not exists(setup_location):
                    raise BuildInterruptingException(
                        "Could not find Setup.dist or Setup in Python build")

            shprint(sh.make, '-j', str(cpu_count()), '-C', build_dir)

            # make a copy of the python executable giving it the name we want,
            # because we got different python's executable names depending on
            # the fs being case-insensitive (Mac OS X, Cygwin...) or
            # case-sensitive (linux)...so this way we will have an unique name
            # for our hostpython, regarding the used fs
            for exe_name in ['python.exe', 'python']:
                exe = join(self.get_path_to_python(), exe_name)
                if isfile(exe):
                    shprint(sh.cp, exe, self.python_exe)
                    break

        self.ctx.hostpython = self.python_exe


recipe = Hostpython3Recipe()
