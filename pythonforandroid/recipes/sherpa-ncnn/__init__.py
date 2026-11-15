from multiprocessing import cpu_count
from os.path import join

import sh

from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import Recipe


class SherpaNcnnRecipe(Recipe):
    name = "sherpa-ncnn"
    version = '2.1.15'
    url = 'https://github.com/k2-fsa/sherpa-ncnn/archive/refs/tags/v{version}.tar.gz'
    built_libraries = {
        'libncnn.so': 'build/install/lib',
        'libsherpa-ncnn-jni.so': 'build/install/lib',
    }

    def build_arch(self, arch):
        source_dir = self.get_build_dir(arch.arch)
        build_dir = join(source_dir, 'build')
        install_dir = join(build_dir, 'install')
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
                    '-DBUILD_SHARED_LIBS=ON',
                    '-DSHERPA_NCNN_ENABLE_PORTAUDIO=OFF',
                    '-DSHERPA_NCNN_ENABLE_BINARY=OFF',
                    '-DSHERPA_NCNN_ENABLE_TEST=OFF',
                    '-DSHERPA_NCNN_ENABLE_C_API=OFF',
                    '-DSHERPA_NCNN_ENABLE_GENERATE_INT8_SCALE_TABLE=OFF',
                    _env=env)
            shprint(sh.make, f'-j{cpu_count()}', _env=env)
            shprint(sh.make, 'install/strip', _env=env)


recipe = SherpaNcnnRecipe()
