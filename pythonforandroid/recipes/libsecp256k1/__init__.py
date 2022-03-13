from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
from pythonforandroid.recipe import Recipe
from multiprocessing import cpu_count
from os.path import exists
import sh


class LibSecp256k1Recipe(Recipe):

    built_libraries = {'libsecp256k1.so': '.libs'}

    url = 'https://github.com/bitcoin-core/secp256k1/archive/master.zip'

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            if not exists('configure'):
                shprint(sh.Command('./autogen.sh'), _env=env)
            shprint(
                sh.Command('./configure'),
                '--host=' + arch.command_prefix,
                '--prefix=' + self.ctx.get_python_install_dir(arch.arch),
                '--enable-shared',
                '--enable-module-recovery',
                '--enable-experimental',
                '--enable-module-ecdh',
                _env=env)
            shprint(sh.make, '-j' + str(cpu_count()), _env=env)


recipe = LibSecp256k1Recipe()
