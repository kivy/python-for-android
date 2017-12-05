
from pythonforandroid.toolchain import Recipe, shprint, current_directory, info, warning
from os.path import join, exists
from os import chdir
import os
import sh


class Hostpython2Recipe(Recipe):
    version = '2.7.2'
    url = 'https://python.org/ftp/python/{version}/Python-{version}.tar.bz2'
    name = 'hostpython2'

    conflicts = ['hostpython3']

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
                self.ctx.hostpython = join(self.get_build_dir(),
                                           'hostpython')
                self.ctx.hostpgen = join(self.get_build_dir(),
                                           'hostpgen')
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


recipe = Hostpython2Recipe()
