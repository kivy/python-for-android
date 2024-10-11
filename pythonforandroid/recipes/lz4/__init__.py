from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
from pythonforandroid.toolchain import current_directory
from os.path import join
import sh
import os


class LibLz4Recipe(Recipe):
    name = 'liblz4'
    version = '1.9.4'  # Update to the desired version
    url = 'https://github.com/lz4/lz4/archive/refs/tags/v{version}.tar.gz'
    built_libraries = {'liblz4.a': '.'}

    def build_arch(self, arch):
        super().build_arch(arch)
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)
        lib_dir = self.ctx.get_libs_dir(arch.arch)
        include_dir = join(self.ctx.get_python_install_dir(), 'include', 'lz4')

        # Ensure include directory exists
        if not os.path.exists(include_dir):
            os.makedirs(include_dir)

        # Build the library
        with current_directory(join(build_dir, 'lib')):
            # Clean previous builds
            shprint(sh.make, 'clean', _env=env)
            # Build the static library
            shprint(sh.make, 'liblz4.a', _env=env)
            # Copy the static library
            shprint(sh.cp, '-v', 'liblz4.a', lib_dir)
            # Copy headers
            shprint(sh.cp, '-v', 'lz4.h', include_dir)

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
        # Set compiler flags if needed
        return env


recipe = LibLz4Recipe()
