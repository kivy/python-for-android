from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from multiprocessing import cpu_count
from os.path import realpath
import sh


class LibX264Recipe(Recipe):
    version = 'x264-snapshot-20171218-2245-stable'  # using mirror url since can't use ftp
    url = 'http://mirror.yandex.ru/mirrors/ftp.videolan.org/x264/snapshots/{version}.tar.bz2'
    built_libraries = {'libx264.a': 'lib'}

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            if 'arm64' in arch.arch:
                cross_prefix = 'aarch64-linux-android-'
            else:
                cross_prefix = 'arm-linux-androideabi-'
            configure = sh.Command('./configure')
            shprint(configure,
                    '--cross-prefix={}'.format(cross_prefix),
                    '--host=arm-linux',
                    '--disable-asm',
                    '--disable-cli',
                    '--enable-pic',
                    '--disable-shared',
                    '--enable-static',
                    '--prefix={}'.format(realpath('.')),
                    _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)
            shprint(sh.make, 'install', _env=env)


recipe = LibX264Recipe()
