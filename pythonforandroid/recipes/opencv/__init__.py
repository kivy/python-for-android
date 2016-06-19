import os
import sh
from pythonforandroid.toolchain import (
    NDKRecipe,
    Recipe,
    current_directory,
    info,
    shprint,
)
from multiprocessing import cpu_count


class OpenCVRecipe(NDKRecipe):
    version = '2.4.10.1'
    url = 'https://github.com/Itseez/opencv/archive/{version}.zip'
    #md5sum = '2ddfa98e867e6611254040df841186dc'
    depends = ['numpy']
    patches = ['patches/p4a_build-2.4.10.1.patch']
    generated_libraries = ['cv2.so']
    
    def prebuild_arch(self, arch):
        self.apply_patches(arch)
        
    def get_recipe_env(self,arch):
        env = super(OpenCVRecipe, self).get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['ANDROID_NDK'] = self.ctx.ndk_dir
        env['ANDROID_SDK'] = self.ctx.sdk_dir
        env['SITEPACKAGES_PATH'] = self.ctx.get_site_packages_dir()
        return env

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            cvsrc = self.get_build_dir(arch.arch)
            lib_dir = os.path.join(self.ctx.get_python_install_dir(), "lib")
            
            shprint(sh.cmake,
                '-DP4A=ON','-DANDROID_ABI={}'.format(arch.arch),
                '-DCMAKE_TOOLCHAIN_FILE={}/platforms/android/android.toolchain.cmake'.format(cvsrc),
                '-DPYTHON_INCLUDE_PATH={}/include/python2.7'.format(env['PYTHON_ROOT']),
                '-DPYTHON_LIBRARY={}/lib/libpython2.7.so'.format(env['PYTHON_ROOT']),
                '-DPYTHON_NUMPY_INCLUDE_DIR={}/numpy/core/include'.format(env['SITEPACKAGES_PATH']),
                '-DANDROID_EXECUTABLE={}/tools/android'.format(env['ANDROID_SDK']),                    
                '-DBUILD_TESTS=OFF', '-DBUILD_PERF_TESTS=OFF', '-DBUILD_EXAMPLES=OFF', '-DBUILD_ANDROID_EXAMPLES=OFF',
                '-DPYTHON_PACKAGES_PATH={}'.format(env['SITEPACKAGES_PATH']),
                cvsrc,
            _env=env)
            shprint(sh.make,'-j',str(cpu_count()),'opencv_python')
            shprint(sh.cmake,'-DCOMPONENT=python','-P','./cmake_install.cmake')
            sh.cp('-a',sh.glob('./lib/{}/lib*.so'.format(arch.arch)),lib_dir)

recipe = OpenCVRecipe()
