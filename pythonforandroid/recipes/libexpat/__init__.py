
import sh
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from os.path import join
from multiprocessing import cpu_count


class LibexpatRecipe(Recipe):
    version = 'master'
    url = 'https://github.com/libexpat/libexpat/archive/{version}.zip'
    built_libraries = {'libexpat.so': 'dist/lib'}
    depends = []

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(join(self.get_build_dir(arch.arch), 'expat')):
            dst_dir = join(self.get_build_dir(arch.arch), 'dist')
            shprint(sh.Command('./buildconf.sh'), _env=env)
            shprint(
                sh.Command('./configure'),
                '--host={}'.format(arch.command_prefix),
                '--enable-shared',
                '--without-xmlwf',
                '--prefix={}'.format(dst_dir),
                _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)
            shprint(sh.make, 'install', _env=env)


recipe = LibexpatRecipe()
