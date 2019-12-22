from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
from os.path import join
import sh


class LibZMQRecipe(Recipe):
    version = '4.3.2'
    url = 'https://github.com/zeromq/libzmq/releases/download/v{version}/zeromq-{version}.zip'
    depends = []
    built_libraries = {'libzmq.so': 'src/.libs'}
    need_stl_shared = True

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        #
        # libsodium_recipe = Recipe.get_recipe('libsodium', self.ctx)
        # libsodium_dir = libsodium_recipe.get_build_dir(arch.arch)
        # env['sodium_CFLAGS'] = '-I{}'.format(join(
        #     libsodium_dir, 'src'))
        # env['sodium_LDLAGS'] = '-L{}'.format(join(
        #     libsodium_dir, 'src', 'libsodium', '.libs'))

        curdir = self.get_build_dir(arch.arch)
        prefix = join(curdir, "install")

        with current_directory(curdir):
            bash = sh.Command('sh')
            shprint(
                bash, './configure',
                '--host={}'.format(arch.command_prefix),
                '--without-documentation',
                '--prefix={}'.format(prefix),
                '--with-libsodium=no',
                '--disable-libunwind',
                _env=env)
            shprint(sh.make, _env=env)
            shprint(sh.make, 'install', _env=env)


recipe = LibZMQRecipe()
