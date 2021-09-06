from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
import sh
from multiprocessing import cpu_count
from os.path import join


class LibpcreRecipe(Recipe):
    version = '8.44'
    url = 'https://ftp.pcre.org/pub/pcre/pcre-{version}.tar.bz2'

    built_libraries = {'libpcre.so': '.libs'}

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            shprint(
                sh.Command('./configure'),
                *'''--host=arm-linux-androideabi
                    --disable-cpp --enable-jit --enable-utf8
                    --enable-unicode-properties'''.split(),
                _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)

    def get_lib_dir(self, arch):
        return join(self.get_build_dir(arch), '.libs')


recipe = LibpcreRecipe()
