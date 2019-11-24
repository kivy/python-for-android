from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from multiprocessing import cpu_count
from os.path import realpath
import sh


class LibShineRecipe(Recipe):
    version = 'c72aba9031bde18a0995e7c01c9b53f2e08a0e46'
    url = 'https://github.com/toots/shine/archive/{version}.zip'

    built_libraries = {'libshine.so': 'lib'}

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        # technically, libraries should go to `LDLIBS`, but it seems
        # that libshine doesn't like so, and it will fail on linking stage
        env['LDLIBS'] = env['LDLIBS'].replace(' -lm', '')
        env['LDFLAGS'] += ' -lm'
        return env

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            shprint(sh.Command('./bootstrap'))
            configure = sh.Command('./configure')
            shprint(configure,
                    f'--host={arch.command_prefix}',
                    '--enable-pic',
                    '--disable-static',
                    '--enable-shared',
                    f'--prefix={realpath(".")}',
                    _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)
            shprint(sh.make, 'install', _env=env)


recipe = LibShineRecipe()
