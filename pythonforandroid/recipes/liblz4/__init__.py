from pythonforandroid.logger import shprint
from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory
from os.path import join
import sh
import os

class LibLZ4Recipe(Recipe):
    name = 'liblz4'
    version = '1.9.4'  # Use the desired version
    url = 'https://github.com/lz4/lz4/archive/refs/tags/v{version}.tar.gz'
    depends = []

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)
        lib_dir = self.ctx.get_libs_dir(arch.arch)
        include_dir = join(self.ctx.get_python_install_dir(), 'include', 'lz4')

        # Ensure include directory exists
        if not os.path.exists(include_dir):
            os.makedirs(include_dir)

        with current_directory(join(build_dir, 'lib')):
            # Clean previous builds
            shprint(sh.make, 'clean', _env=env)
            # Build the static library
            shprint(sh.make, 'CC={}'.format(env['CC']), 'liblz4.a', _env=env)
            # Copy the static library to the libs directory
            sh.cp('liblz4.a', lib_dir)
            # Copy headers to the include directory
            sh.cp('lz4.h', include_dir)
            sh.cp('lz4frame.h', include_dir)
            sh.cp('lz4hc.h', include_dir)
            sh.cp('xxhash.h', include_dir)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # Ensure the correct compiler is used
        python_recipe = self.get_recipe('python3', self.ctx)
        env['CC'] = python_recipe.get_recipe_env(arch)['CC']
        return env

recipe = LibLZ4Recipe()
