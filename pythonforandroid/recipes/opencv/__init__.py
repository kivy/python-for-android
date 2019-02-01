import os
import sh
from pythonforandroid.recipe import NDKRecipe
from pythonforandroid.toolchain import (
    current_directory,
    shprint,
)
from multiprocessing import cpu_count


class OpenCVRecipe(NDKRecipe):
    version = '4.0.1'
    url = 'https://github.com/opencv/opencv/archive/{version}.zip'
    depends = ['numpy']

    def get_recipe_env(self, arch):
        env = super(OpenCVRecipe, self).get_recipe_env(arch)
        env['ANDROID_NDK'] = self.ctx.ndk_dir
        env['ANDROID_SDK'] = self.ctx.sdk_dir
        return env

    def should_build(self, arch):
        return True

    def build_arch(self, arch):
        build_dir = os.path.join(self.get_build_dir(arch.arch), 'build')
        shprint(sh.mkdir, '-p', build_dir)
        with current_directory(build_dir):
            env = self.get_recipe_env(arch)
            shprint(sh.cmake,
                    '-DANDROID_ABI={}'.format(arch.arch),
                    '-DCMAKE_TOOLCHAIN_FILE={}/build/cmake/android.toolchain.cmake'.format(self.ctx.ndk_dir),
                    '-DPYTHON_NUMPY_INCLUDE_DIR={}/numpy/core/include'.format(self.ctx.get_site_packages_dir()),
                    '-DANDROID_EXECUTABLE={}/tools/android'.format(env['ANDROID_SDK']),
                    '-DBUILD_TESTS=OFF', '-DBUILD_PERF_TESTS=OFF', '-DENABLE_TESTING=OFF',
                    '-DBUILD_EXAMPLES=OFF', '-DBUILD_ANDROID_EXAMPLES=OFF',
                    '-DBUILD_opencv_imgproc=OFF', '-DBUILD_opencv_flann=OFF',
                    '-DBUILD_opencv_python3=ON',
                    '-DBUILD_WITH_STANDALONE_TOOLCHAIN=ON',
                    '-DPYTHON_PACKAGES_PATH={}'.format(self.ctx.get_site_packages_dir()),
                    '-DANDROID_STANDALONE_TOOLCHAIN={}'.format(self.ctx.ndk_dir),
                    '-DANDROID_NATIVE_API_LEVEL={}'.format(self.ctx.android_api),
                    self.get_build_dir(arch.arch),
                    _env=env)
            shprint(sh.make, '-j', str(cpu_count()))
            shprint(sh.cmake, '-DCOMPONENT=python', '-P', './cmake_install.cmake')
            sh.cp('-a', sh.glob('./lib/{}/lib*.a'.format(arch.arch)), self.ctx.get_libs_dir(arch.arch))
            self.ctx.get_libs_dir(arch.arch)


recipe = OpenCVRecipe()
