
from pythonforandroid.toolchain import Recipe, shprint, current_directory, info, warning
from os.path import join, exists
from os import chdir
import sh


class Hostpython3Recipe(Recipe):
    version = '3.5'
    # url = 'http://python.org/ftp/python/{version}/Python-{version}.tgz'
    url = 'https://github.com/crystax/android-vendor-python-3-5/archive/master.zip'
    name = 'hostpython3'

    conflicts = ['hostpython2']

    # def prebuild_armeabi(self):
    #     # Override hostpython Setup?
    #     shprint(sh.cp, join(self.get_recipe_dir(), 'Setup'),
    #             join(self.get_build_dir('armeabi'), 'Modules', 'Setup'))

    def build_arch(self, arch):
        # AND: Should use an i386 recipe system
        warning('Running hostpython build. Arch is armeabi! '
                'This is naughty, need to fix the Arch system!')

        # AND: Fix armeabi again
        with current_directory(self.get_build_dir(arch.arch)):

            if exists('hostpython'):
                info('hostpython already exists, skipping build')
                self.ctx.hostpython = join(self.get_build_dir('armeabi'),
                                           'hostpython')
                self.ctx.hostpgen = join(self.get_build_dir('armeabi'),
                                         'hostpgen')
                return
            
            configure = sh.Command('./configure')

            shprint(configure)
            shprint(sh.make, '-j5', 'BUILDPYTHON=hostpython', 'hostpython',
                    'PGEN=Parser/hostpgen', 'Parser/hostpgen')

            shprint(sh.mv, join('Parser', 'hostpgen'), 'hostpgen')

            # if exists('python.exe'):
            #     shprint(sh.mv, 'python.exe', 'hostpython')
            # elif exists('python'):
            #     shprint(sh.mv, 'python', 'hostpython')
            if exists('hostpython'):
                pass  # The above commands should automatically create
                      # the hostpython binary, unlike with python2
            else:
                warning('Unable to find the python executable after '
                        'hostpython build! Exiting.')
                exit(1)

        self.ctx.hostpython = join(self.get_build_dir(arch.arch), 'hostpython')
        self.ctx.hostpgen = join(self.get_build_dir(arch.arch), 'hostpgen')


recipe = Hostpython3Recipe()
