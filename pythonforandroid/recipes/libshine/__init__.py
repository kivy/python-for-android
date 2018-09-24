from pythonforandroid.toolchain import Recipe, current_directory, shprint
from os.path import exists, join, realpath
import sh


class LibShineRecipe(Recipe):
    version = 'c72aba9031bde18a0995e7c01c9b53f2e08a0e46'
    url = 'https://github.com/toots/shine/archive/{version}.zip'

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
