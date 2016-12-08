from pythonforandroid.toolchain import Recipe, shprint, current_directory, ArchARM
from os.path import exists, join, realpath
from os import uname
import glob
import sh


class LibX264Recipe(Recipe):
    version = 'last_stable'
    url = 'http://mirror.yandex.ru/mirrors/ftp.videolan.org/x264/snapshots/{version}_x264.tar.bz2'

    # TODO add should_build(self, arch)

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            configure = sh.Command('./configure')
            shprint(configure,
                    '--cross-prefix=arm-linux-androideabi-',
                    '--host=arm-linux',
                    '--disable-asm',
                    '--disable-cli',
                    '--enable-pic',
                    '--disable-shared',
                    '--enable-static',
                    '--prefix={}'.format(realpath('.')),
                    _env=env)
            shprint(sh.make, '-j4', _env=env)
            shprint(sh.make, 'install', _env=env)

recipe = LibX264Recipe()
