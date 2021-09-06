from multiprocessing import cpu_count
from os.path import join

import sh

from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.toolchain import shprint
from pythonforandroid.recipe import Recipe


class LibwebpRecipe(Recipe):
    version = '1.1.0'
    url = 'https://storage.googleapis.com/downloads.webmproject.org/releases/webp/libwebp-{version}.tar.gz'  # noqa
    depends = []
    built_libraries = {
        'libwebp.so': 'installation/lib',
        'libwebpdecoder.so': 'installation/lib',
        'libwebpdemux.so': 'installation/lib',
        'libwebpmux.so': 'installation/lib',
    }

    def build_arch(self, arch):
        source_dir = self.get_build_dir(arch.arch)
        build_dir = join(source_dir, 'build')
        install_dir = join(source_dir, 'installation')
        toolchain_file = join(
            self.ctx.ndk_dir, 'build', 'cmake', 'android.toolchain.cmake',
        )

        ensure_dir(build_dir)
        with current_directory(build_dir):
            env = self.get_recipe_env(arch)
            shprint(sh.cmake, source_dir,
                    f'-DANDROID_ABI={arch.arch}',
                    f'-DANDROID_NATIVE_API_LEVEL={self.ctx.ndk_api}',

                    f'-DCMAKE_TOOLCHAIN_FILE={toolchain_file}',
                    f'-DCMAKE_INSTALL_PREFIX={install_dir}',
                    '-DCMAKE_BUILD_TYPE=Release',

                    '-DBUILD_SHARED_LIBS=1',

                    _env=env)
            shprint(sh.make, '-j' + str(cpu_count()), _env=env)
            # We make the install because this way we will have
            # all the includes and libraries in one place
            shprint(sh.make, 'install', _env=env)


recipe = LibwebpRecipe()
