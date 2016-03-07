
from pythonforandroid.toolchain import Recipe, shprint, current_directory, info, warning
from os.path import join, exists
from os import environ
import sh


class Hostpython2Recipe(Recipe):
    version = '2.7.9'
    url = 'http://python.org/ftp/python/{version}/Python-{version}.tgz'  # tar.bz2'
    name = 'hostpython2'

    conflicts = ['hostpython3']

    def get_recipe_env(self, arch):
        env = super(Hostpython2Recipe, self).get_recipe_env(arch)
        env['CFLAGS'] = ' '.join([env['CFLAGS'], '-Wformat'])
        return env

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
        # Hack to make it work from user recipes, referenced on python-for-android issues  #613
        # recipe_dir = self.get_recipe(self.name, arch.arch).recipe_dir
        # shprint(sh.cp, join(recipe_dir, 'Setup'), join(self.get_build_dir(), 'Modules', 'Setup'))


    def build_arch(self, arch):

        with current_directory(self.get_build_dir()):
            if exists('hostpython'):
                info('Setting ctx hostpython from previous build...')
                self.ctx.hostpython = join(self.get_build_dir(), 'hostpython')
                self.ctx.hostpgen = join(self.get_build_dir(), 'hostpgen')
            else:
                info('Must build hostpython...')
                self.do_build_arch(arch)

    def do_build_arch(self, arch):
        env = dict(environ)
        with current_directory(self.get_build_dir()):
            if exists('hostpython'):
                info('hostpython already exists, skipping build')
                self.ctx.hostpython = join(self.get_build_dir(),
                                           'hostpython')
                self.ctx.hostpgen = join(self.get_build_dir(),
                                           'hostpgen')
                return

            configure = sh.Command('./configure')

            shprint(configure, _env=env)
            shprint(sh.make, '-j5', _env=env)

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
