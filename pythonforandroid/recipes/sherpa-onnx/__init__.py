from multiprocessing import cpu_count
from os.path import join

import sh

from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import Recipe


class SherpaOnnxRecipe(Recipe):
    name = "sherpa-onnx"
    version = '1.12.38'
    url = 'https://github.com/k2-fsa/sherpa-onnx/archive/refs/tags/v{version}.tar.gz'
    depends = ['libonnxruntime']
    built_libraries = {
        'libsherpa-onnx-jni.so': 'build/install/lib',
    }

    def build_arch(self, arch):
        source_dir = self.get_build_dir(arch.arch)
        build_dir = join(source_dir, 'build')
        install_dir = join(build_dir, 'install')
        toolchain_file = join(
            self.ctx.ndk_dir, 'build', 'cmake', 'android.toolchain.cmake',
        )

        ort_recipe = self.get_recipe('libonnxruntime', self.ctx)
        ort_lib_dir = ort_recipe.get_lib_dir(arch)
        ort_include_dir = ort_recipe.get_include_dir(arch)

        ensure_dir(build_dir)
        with current_directory(build_dir):
            env = self.get_recipe_env(arch)
            env['SHERPA_ONNXRUNTIME_LIB_DIR'] = ort_lib_dir
            env['SHERPA_ONNXRUNTIME_INCLUDE_DIR'] = ort_include_dir

            shprint(sh.cmake, source_dir,
                    f'-DANDROID_ABI={arch.arch}',
                    f'-DANDROID_NATIVE_API_LEVEL={self.ctx.ndk_api}',
                    f'-DCMAKE_TOOLCHAIN_FILE={toolchain_file}',
                    f'-DCMAKE_INSTALL_PREFIX={install_dir}',
                    '-DCMAKE_BUILD_TYPE=Release',
                    '-DBUILD_SHARED_LIBS=ON',
                    '-DSHERPA_ONNX_ENABLE_BINARY=OFF',
                    '-DSHERPA_ONNX_ENABLE_PYTHON=OFF',
                    '-DSHERPA_ONNX_ENABLE_TESTS=OFF',
                    '-DSHERPA_ONNX_ENABLE_CHECK=OFF',
                    '-DSHERPA_ONNX_ENABLE_PORTAUDIO=OFF',
                    '-DSHERPA_ONNX_ENABLE_C_API=OFF',
                    '-DSHERPA_ONNX_ENABLE_WEBSOCKET=OFF',
                    '-DSHERPA_ONNX_LINK_LIBSTDCPP_STATICALLY=OFF',
                    _env=env)
            shprint(sh.make, f'-j{cpu_count()}', _env=env)
            shprint(sh.make, 'install/strip', _env=env)


recipe = SherpaOnnxRecipe()
