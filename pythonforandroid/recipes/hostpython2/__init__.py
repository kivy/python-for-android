
from toolchain import Recipe, shprint, get_directory, current_directory, info, warning
from os.path import join, exists
from os import chdir
import sh


class Hostpython2Recipe(Recipe):
    version = '2.7.2'
    url = 'http://python.org/ftp/python/{version}/Python-{version}.tar.bz2'
    name = 'hostpython2'

    def prebuild_armeabi(self):
        # Override hostpython Setup?
        shprint(sh.cp, join(self.get_recipe_dir(), 'Setup'),
                join(self.get_build_dir('armeabi'), 'Modules', 'Setup'))

    def build_armeabi(self):
        # AND: Should use an i386 recipe system
        warning('Running hostpython build. Arch is armeabi! '
                'This is naughty, need to fix the Arch system!')

        # AND: Fix armeabi again
        with current_directory(self.get_build_dir('armeabi')):

            if exists('hostpython'):
                info('hostpython already exists, skipping build')
                self.ctx.hostpython = join(self.get_build_dir('armeabi'),
                                           'hostpython')
                self.ctx.hostpgen = join(self.get_build_dir('armeabi'),
                                           'hostpgen')
                return
            
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

        self.ctx.hostpython = join(self.get_build_dir('armeabi'), 'hostpython')
        self.ctx.hostpgen = join(self.get_build_dir('armeabi'), 'hostpgen')


recipe = Hostpython2Recipe()
