from pythonforandroid.toolchain import Recipe, shprint, current_directory, ArchARM
from os.path import exists, join, realpath
from os import uname
import glob
import sh


class LibShineRecipe(Recipe):
    version = '20aee967f67abefd065c196eec7ce21adbbe1549'
    url = 'https://github.com/toots/shine/archive/{version}.zip'
    md5sum = 'bbf1f657e6adccb5e79f59da9ecfac2d'

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
