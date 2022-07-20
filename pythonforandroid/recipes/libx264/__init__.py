from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from multiprocessing import cpu_count
from os.path import realpath
import sh


class LibX264Recipe(Recipe):
    version = '5db6aa6cab1b146e07b60cc1736a01f21da01154'  # commit of latest known stable version
    url = 'https://code.videolan.org/videolan/x264/-/archive/{version}/x264-{version}.zip'
    built_libraries = {'libx264.a': 'lib'}

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            configure = sh.Command('./configure')
            shprint(configure,
                    f'--host={arch.command_prefix}',
                    '--disable-asm',
                    '--disable-cli',
                    '--enable-pic',
                    '--enable-static',
                    '--prefix={}'.format(realpath('.')),
                    _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)
            shprint(sh.make, 'install', _env=env)


recipe = LibX264Recipe()
