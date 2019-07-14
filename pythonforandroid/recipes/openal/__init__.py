from pythonforandroid.recipe import NDKRecipe
from pythonforandroid.toolchain import current_directory, shprint
from os.path import join
import os
import sh


class OpenALRecipe(NDKRecipe):
    version = '1.18.2'
    url = 'https://github.com/kcat/openal-soft/archive/openal-soft-{version}.tar.gz'

    generated_libraries = ['libopenal.so']

    def prebuild_arch(self, arch):
        # we need to build native tools for host system architecture
        with current_directory(join(self.get_build_dir(arch.arch), 'native-tools')):
            shprint(sh.cmake, '.', _env=os.environ)
            shprint(sh.make, _env=os.environ)

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = self.get_recipe_env(arch)
            cmake_args = [
                '-DCMAKE_TOOLCHAIN_FILE={}'.format('XCompile-Android.txt'),
                '-DHOST={}'.format(self.ctx.toolchain_prefix)
            ]
            shprint(
                sh.cmake, '.',
                *cmake_args,
                _env=env
            )
            shprint(sh.make, _env=env)
            self.install_libs(arch, 'libopenal.so')


recipe = OpenALRecipe()
