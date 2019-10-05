from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
from pythonforandroid.recipe import Recipe
from multiprocessing import cpu_count
import sh


class LibIconvRecipe(Recipe):

    version = '1.15'

    url = 'https://ftp.gnu.org/pub/gnu/libiconv/libiconv-{version}.tar.gz'

    built_libraries = {'libiconv.so': 'lib/.libs'}

    patches = ['libiconv-1.15-no-gets.patch']

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(
                sh.Command('./configure'),
                '--host=' + arch.command_prefix,
                '--prefix=' + self.ctx.get_python_install_dir(),
                _env=env)
            shprint(sh.make, '-j' + str(cpu_count()), _env=env)


recipe = LibIconvRecipe()
