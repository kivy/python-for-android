import os
from pythonforandroid.toolchain import shprint, current_directory
from pythonforandroid.recipe import Recipe
from multiprocessing import cpu_count
import sh


class LibIconvRecipe(Recipe):

    version = '1.15'

    url = 'https://ftp.gnu.org/pub/gnu/libiconv/libiconv-{version}.tar.gz'

    patches = ['libiconv-1.15-no-gets.patch']

    def should_build(self, arch):
        return not os.path.exists(
                os.path.join(self.ctx.get_libs_dir(arch.arch), 'libiconv.so'))

    def build_arch(self, arch):
        super(LibIconvRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(
                sh.Command('./configure'),
                '--host=' + arch.toolchain_prefix,
                '--prefix=' + self.ctx.get_python_install_dir(),
                _env=env)
            shprint(sh.make, '-j' + str(cpu_count()), _env=env)
            libs = ['lib/.libs/libiconv.so']
            self.install_libs(arch, *libs)


recipe = LibIconvRecipe()
