from pythonforandroid.toolchain import Recipe, shprint, current_directory, ArchARM
from os.path import exists, join, realpath
from os import uname
import glob
import sh


class LibShineRecipe(Recipe):
    version = 'b403b3e8a41377e0576d834b179a5cc7096ff548'  # we need master brnch
    url = 'https://github.com/toots/shine/archive/{version}.zip'
    md5sum = '24cf9488d06f7acf0a0fbb162cc587ab'

    def should_build(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        return not exists(join(build_dir, 'lib', 'libshine.a'))

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            shprint(sh.Command('./bootstrap'))
            configure = sh.Command('./configure')
            shprint(configure,
                    '--host=arm-linux',
                    '--enable-pic',
                    '--disable-shared',
                    '--enable-static',
                    '--prefix={}'.format(realpath('.')),
                    _env=env)
            shprint(sh.make, '-j4', _env=env)
            shprint(sh.make, 'install', _env=env)

recipe = LibShineRecipe()
