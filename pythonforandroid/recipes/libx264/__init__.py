from pythonforandroid.toolchain import Recipe, current_directory, shprint
from os.path import exists, join, realpath
import sh


class LibX264Recipe(Recipe):
    version = 'x264-snapshot-20171218-2245-stable'  # using mirror url since can't use ftp
    url = 'http://mirror.yandex.ru/mirrors/ftp.videolan.org/x264/snapshots/{version}.tar.bz2'

    def should_build(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        return not exists(join(build_dir, 'lib', 'libx264.a'))

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
