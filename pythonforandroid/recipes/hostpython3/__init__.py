from pythonforandroid.toolchain import Recipe, shprint, info, warning
from pythonforandroid.util import ensure_dir, current_directory
from os.path import join, exists
import os
import sh


class Hostpython3Recipe(Recipe):
    version = 'bpo-30386'
    url = 'https://github.com/inclement/cpython/archive/{version}.zip'
    name = 'hostpython3'

    conflicts = ['hostpython2']

    def get_build_container_dir(self, arch=None):
        choices = self.check_recipe_choices()
        dir_name = '-'.join([self.name] + choices)
        return join(self.ctx.build_dir, 'other_builds', dir_name, 'desktop')

    def get_build_dir(self, arch=None):
        # Unlike other recipes, the hostpython build dir doesn't depend on the target arch
        return join(self.get_build_container_dir(), self.name)

    def build_arch(self, arch):
        recipe_build_dir = self.get_build_dir(arch.arch)

        # Create a subdirectory to actually perform the build
        build_dir = join(recipe_build_dir, 'native-build')
        ensure_dir(build_dir)

        if not exists(join(build_dir, 'python')):
            with current_directory(recipe_build_dir):
                env = {}  # The command line environment we will use


                # Configure the build
                with current_directory(build_dir):
                    if not exists('config.status'):
                        shprint(sh.Command(join(recipe_build_dir, 'configure')))

                # Create the Setup file. This copying from Setup.dist
                # seems to be the normal and expected procedure.
                assert exists(join(build_dir, 'Modules')), (
                    'Expected dir {} does not exist'.format(join(build_dir, 'Modules')))
                shprint(sh.cp, join('Modules', 'Setup.dist'), join(build_dir, 'Modules', 'Setup'))

                result = shprint(sh.make, '-C', build_dir)
        else:
            info('Skipping hostpython3 build as it has already been completed')

        self.ctx.hostpython = join(build_dir, 'python')
        self.ctx.hostpgen = '/usr/bin/false'  # is this actually used for anything?

recipe = Hostpython3Recipe()
