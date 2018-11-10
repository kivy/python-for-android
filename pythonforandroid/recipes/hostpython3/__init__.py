from pythonforandroid.toolchain import Recipe, shprint, info
from pythonforandroid.util import ensure_dir, current_directory
from os.path import join, exists
import sh

BUILD_SUBDIR = 'native-build'


class Hostpython3Recipe(Recipe):
    version = '3.7.1'
    url = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'
    name = 'hostpython3'

    conflicts = ['hostpython2', 'hostpython3crystax']

    def get_build_container_dir(self, arch=None):
        choices = self.check_recipe_choices()
        dir_name = '-'.join([self.name] + choices)
        return join(self.ctx.build_dir, 'other_builds', dir_name, 'desktop')

    def get_build_dir(self, arch=None):
        # Unlike other recipes, the hostpython build dir doesn't depend on the target arch
        return join(self.get_build_container_dir(), self.name)

    def get_path_to_python(self):
        return join(self.get_build_dir(), BUILD_SUBDIR)

    def build_arch(self, arch):
        recipe_build_dir = self.get_build_dir(arch.arch)

        # Create a subdirectory to actually perform the build
        build_dir = join(recipe_build_dir, BUILD_SUBDIR)
        ensure_dir(build_dir)

        if not exists(join(build_dir, 'python')):
            with current_directory(recipe_build_dir):
                # Configure the build
                with current_directory(build_dir):
                    if not exists('config.status'):
                        shprint(sh.Command(join(recipe_build_dir, 'configure')))

                # Create the Setup file. This copying from Setup.dist
                # seems to be the normal and expected procedure.
                shprint(sh.cp, join('Modules', 'Setup.dist'), join(build_dir, 'Modules', 'Setup'))

                result = shprint(sh.make, '-C', build_dir)
        else:
            info('Skipping hostpython3 build as it has already been completed')

        self.ctx.hostpython = join(build_dir, 'python')


recipe = Hostpython3Recipe()
