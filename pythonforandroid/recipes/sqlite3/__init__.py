import sh
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
from pythonforandroid.recipe import Recipe
from multiprocessing import cpu_count


class Sqlite3Recipe(Recipe):
    version = '3.50.4'
    url = 'https://github.com/sqlite/sqlite/archive/refs/tags/version-{version}.tar.gz'
    built_libraries = {'libsqlite3.so': '.'}

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)
        config_args = {
            '--host={}'.format(arch.command_prefix),
            '--prefix={}'.format(build_dir),
            '--disable-tcl',
        }
        with current_directory(build_dir):
            configure = sh.Command('./configure')
            shprint(configure, *config_args, _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)


recipe = Sqlite3Recipe()
