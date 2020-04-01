from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from multiprocessing import cpu_count
import sh


class LibsodiumRecipe(Recipe):
    version = '1.0.16'
    url = 'https://github.com/jedisct1/libsodium/releases/download/{version}/libsodium-{version}.tar.gz'
    depends = []
    patches = ['size_max_fix.patch']
    built_libraries = {'libsodium.so': 'src/libsodium/.libs'}

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            bash = sh.Command('bash')
            shprint(
                bash,
                'configure',
                '--disable-soname-versions',
                '--host={}'.format(arch.command_prefix),
                '--enable-shared',
                _env=env,
            )
            shprint(sh.make, '-j', str(cpu_count()), _env=env)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        env['CFLAGS'] += ' -Os'
        return env


recipe = LibsodiumRecipe()
