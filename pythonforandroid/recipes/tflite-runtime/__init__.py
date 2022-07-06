from pythonforandroid.recipe import PythonRecipe, current_directory, \
    shprint, info_main, warning
from pythonforandroid.logger import error
from os.path import join
import sh


class TFLiteRuntimeRecipe(PythonRecipe):
    ###############################################################
    #
    # tflite-runtime README:
    # https://github.com/Android-for-Python/c4k_tflite_example/blob/main/README.md
    #
    # Recipe build references:
    # https://developer.android.com/ndk/guides/cmake
    # https://developer.android.com/ndk/guides/cpu-arm-neon#cmake
    # https://www.tensorflow.org/lite/guide/build_cmake
    # https://www.tensorflow.org/lite/guide/build_cmake_arm
    #
    # Tested using cmake 3.16.3 probably requires cmake >= 3.13
    #
    # THIS RECIPE DOES NOT BUILD x86_64, USE X86 FOR AN EMULATOR
    #
    ###############################################################

    version = '2.8.0'
    url = 'https://github.com/tensorflow/tensorflow/archive/refs/tags/v{version}.zip'
    depends = ['pybind11', 'numpy']
    patches = ['CMakeLists.patch', 'build_with_cmake.patch']
    site_packages_name = 'tflite-runtime'
    call_hostpython_via_targetpython = False

    def should_build(self, arch):
        name = self.folder_name.replace('-', '_')

        if self.ctx.has_package(name, arch):
            info_main('Python package already exists in site-packages')
            return False
        info_main('{} apparently isn\'t already in site-packages'.format(name))
        return True

    def build_arch(self, arch):
        if arch.arch == 'x86_64':
            warning("******** tflite-runtime x86_64 will not be built *******")
            warning("Expect one of these app run time error messages:")
            warning("ModuleNotFoundError: No module named 'tensorflow'")
            warning("ModuleNotFoundError: No module named 'tflite_runtime'")
            warning("Use x86 not x86_64")
            return

        env = self.get_recipe_env(arch)

        # Directories
        root_dir = self.get_build_dir(arch.arch)
        script_dir = join(root_dir,
                          'tensorflow', 'lite', 'tools', 'pip_package')
        build_dir = join(script_dir, 'gen', 'tflite_pip', 'python3')

        # Includes
        python_include_dir = self.ctx.python_recipe.include_root(arch.arch)
        pybind11_recipe = self.get_recipe('pybind11', self.ctx)
        pybind11_include_dir = pybind11_recipe.get_include_dir(arch)
        numpy_include_dir = join(self.ctx.get_site_packages_dir(arch),
                                 'numpy', 'core', 'include')
        includes = ' -I' + python_include_dir + \
                   ' -I' + numpy_include_dir + \
                   ' -I' + pybind11_include_dir

        # Scripts
        build_script = join(script_dir, 'build_pip_package_with_cmake.sh')
        toolchain = join(self.ctx.ndk_dir,
                         'build', 'cmake', 'android.toolchain.cmake')

        # Build
        ########
        with current_directory(root_dir):
            env.update({
                'TENSORFLOW_TARGET': 'android',
                'CMAKE_TOOLCHAIN_FILE': toolchain,
                'ANDROID_PLATFORM': str(self.ctx.ndk_api),
                'ANDROID_ABI': arch.arch,
                'WRAPPER_INCLUDES': includes,
                'CMAKE_SHARED_LINKER_FLAGS': env['LDFLAGS'],
            })

            try:
                info_main('tflite-runtime is building...')
                info_main('Expect this to take at least 5 minutes...')
                cmd = sh.Command(build_script)
                cmd(_env=env)
            except sh.ErrorReturnCode as e:
                error(str(e.stderr))
                exit(1)

        # Install
        ##########
        info_main('Installing tflite-runtime into site-packages')
        with current_directory(build_dir):
            hostpython = sh.Command(self.hostpython_location)
            install_dir = self.ctx.get_python_install_dir(arch.arch)
            env['PACKAGE_VERSION'] = self.version
            shprint(hostpython, 'setup.py', 'install', '-O2',
                    '--root={}'.format(install_dir),
                    '--install-lib=.',
                    _env=env)


recipe = TFLiteRuntimeRecipe()
