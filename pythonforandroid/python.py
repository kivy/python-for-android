from os.path import exists, join
import sh

from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import info, shprint
from pythonforandroid.util import current_directory, ensure_dir


class HostPythonRecipe(Recipe):
    '''
    This is the base class for hostpython3 and hostpython2 recipes. This class
    will take care to do all the work to build a hostpython recipe but, be
    careful, it is intended to be subclassed because some of the vars needs to
    be set:

        - :attr:`name`
        - :attr:`version`

    .. versionadded:: 0.6.0
        Refactored from the hostpython3's recipe by inclement
    '''

    name = ''
    '''The hostpython's recipe name. This should be ``hostpython2`` or
    ``hostpython3``

    .. warning:: This must be set in inherited class.'''

    version = ''
    '''The hostpython's recipe version.

    .. warning:: This must be set in inherited class.'''

    build_subdir = 'native-build'
    '''Specify the sub build directory for the hostpython recipe. Defaults
    to ``native-build``.'''

    url = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'
    '''The default url to download our host python recipe. This url will
    change depending on the python version set in attribute :attr:`version`.'''

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

        if not exists(join(build_dir, 'python')):
            with current_directory(recipe_build_dir):
                # Configure the build
                with current_directory(build_dir):
                    if not exists('config.status'):
                        shprint(
                            sh.Command(join(recipe_build_dir, 'configure')))

                # Create the Setup file. This copying from Setup.dist
                # seems to be the normal and expected procedure.
                shprint(sh.cp, join('Modules', 'Setup.dist'),
                        join(build_dir, 'Modules', 'Setup'))

                result = shprint(sh.make, '-C', build_dir)
        else:
            info('Skipping {name} ({version}) build, as it has already '
                 'been completed'.format(name=self.name, version=self.version))

        self.ctx.hostpython = join(build_dir, 'python')
