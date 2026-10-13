from multiprocessing import cpu_count
from os.path import join

import sh

from pythonforandroid.util import current_directory, ensure_dir
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import Recipe


class LibOnnxRuntimeRecipe(Recipe):
    name = "libonnxruntime"
    version = '1.24.4'
    url = 'https://github.com/microsoft/onnxruntime/archive/refs/tags/v{version}.tar.gz'
    built_libraries = {'libonnxruntime.so': 'build'}
    patches = ['patches/mlasi_bfloat.patch', 'patches/cse_arm32_alignment.patch']

    def build_arch(self, arch):
        source_dir = self.get_build_dir(arch.arch)
        build_dir = join(source_dir, 'build')
        cmake_dir = join(source_dir, 'cmake')
        toolchain_file = join(
            self.ctx.ndk_dir, 'build', 'cmake', 'android.toolchain.cmake',
        )

        ensure_dir(build_dir)
        with current_directory(build_dir):
            env = self.get_recipe_env(arch)
            shprint(sh.cmake, cmake_dir,
                    f'-DANDROID_ABI={arch.arch}',
                    f'-DANDROID_NATIVE_API_LEVEL={self.ctx.ndk_api}',
                    f'-DCMAKE_TOOLCHAIN_FILE={toolchain_file}',
                    '-DCMAKE_BUILD_TYPE=Release',
                    '-Donnxruntime_BUILD_SHARED_LIB=ON',
                    '-Donnxruntime_ENABLE_PYTHON=OFF',
                    '-Donnxruntime_BUILD_UNIT_TESTS=OFF',
                    '-Donnxruntime_USE_NNAPI_BUILTIN=ON',
                    _env=env)
            shprint(sh.make, f'-j{cpu_count()}', _env=env)

    def get_include_dir(self, arch):
        """Headers dir containing onnxruntime_c_api.h for sherpa-onnx."""
        return join(
            self.get_build_dir(arch.arch),
            'include', 'onnxruntime', 'core', 'session',
        )

    def get_lib_dir(self, arch):
        """Dir containing libonnxruntime.so."""
        return join(self.get_build_dir(arch.arch), 'build')


recipe = LibOnnxRuntimeRecipe()
