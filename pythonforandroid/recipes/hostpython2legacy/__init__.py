import os
import sh
from os.path import join, exists

from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import info, warning, shprint
from pythonforandroid.util import current_directory


class Hostpython2LegacyRecipe(Recipe):
    '''
    .. versionadded:: 0.6.0
        This was the original hostpython2's recipe by tito reintroduced as
        hostpython2legacy.
    '''
    version = '2.7.2'
    url = 'https://python.org/ftp/python/{version}/Python-{version}.tar.bz2'
    name = 'hostpython2legacy'
    patches = ['fix-segfault-pygchead.patch']

    conflicts = ['hostpython2', 'hostpython3', 'hostpython3crystax']

    def get_build_container_dir(self, arch=None):
        choices = self.check_recipe_choices()
        dir_name = '-'.join([self.name] + choices)
        return join(self.ctx.build_dir, 'other_builds', dir_name, 'desktop')

    def get_build_dir(self, arch=None):
        return join(self.get_build_container_dir(), self.name)

    def prebuild_arch(self, arch):
        # Override hostpython Setup?
        shprint(sh.cp, join(self.get_recipe_dir(), 'Setup'),
                join(self.get_build_dir(), 'Modules', 'Setup'))

    def build_arch(self, arch):
        with current_directory(self.get_build_dir()):

            if exists('hostpython'):
                info('hostpython already exists, skipping build')
                self.ctx.hostpython = join(self.get_build_dir(), 'hostpython')
                self.ctx.hostpgen = join(self.get_build_dir(), 'hostpgen')
                return

            if 'LIBS' in os.environ:
                os.environ.pop('LIBS')
            configure = sh.Command('./configure')

            shprint(configure)
            shprint(sh.make, '-j5')

            shprint(sh.mv, join('Parser', 'pgen'), 'hostpgen')

            if exists('python.exe'):
                shprint(sh.mv, 'python.exe', 'hostpython')
            elif exists('python'):
                shprint(sh.mv, 'python', 'hostpython')
            else:
                warning('Unable to find the python executable after '
                        'hostpython build! Exiting.')
                exit(1)

        self.ctx.hostpython = join(self.get_build_dir(), 'hostpython')
        self.ctx.hostpgen = join(self.get_build_dir(), 'hostpgen')


recipe = Hostpython2LegacyRecipe()
