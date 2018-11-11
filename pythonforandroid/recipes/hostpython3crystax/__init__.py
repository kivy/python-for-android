from pythonforandroid.toolchain import Recipe, shprint
from os.path import join
import sh


class Hostpython3CrystaXRecipe(Recipe):
    version = 'auto'  # the version is taken from the python3crystax recipe
    name = 'hostpython3crystax'

    conflicts = ['hostpython2']

    def get_build_container_dir(self, arch=None):
        choices = self.check_recipe_choices()
        dir_name = '-'.join([self.name] + choices)
        return join(self.ctx.build_dir, 'other_builds', dir_name, 'desktop')

    # def prebuild_armeabi(self):
    #     # Override hostpython Setup?
    #     shprint(sh.cp, join(self.get_recipe_dir(), 'Setup'),
    #             join(self.get_build_dir('armeabi'), 'Modules', 'Setup'))

    def get_build_dir(self, arch=None):
        return join(self.get_build_container_dir(), self.name)

    def build_arch(self, arch):
        """
        Creates expected build and symlinks system Python version.
        """
        self.ctx.hostpython = '/usr/bin/false'
        # creates the sub buildir (used by other recipes)
        # https://github.com/kivy/python-for-android/issues/1154
        sub_build_dir = join(self.get_build_dir(), 'build')
        shprint(sh.mkdir, '-p', sub_build_dir)
        python3crystax = self.get_recipe('python3crystax', self.ctx)
        system_python = sh.which("python" + python3crystax.version)
        if system_python is None:
            raise OSError(
                ('Trying to use python3crystax=={} but this Python version '
                 'is not installed locally.').format(python3crystax.version))
        link_dest = join(self.get_build_dir(), 'hostpython')
        shprint(sh.ln, '-sf', system_python, link_dest)


recipe = Hostpython3CrystaXRecipe()
