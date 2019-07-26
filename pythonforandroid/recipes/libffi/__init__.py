from os.path import exists, join
from multiprocessing import cpu_count
from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
import sh


class LibffiRecipe(Recipe):
    """
    Requires additional system dependencies on Ubuntu:
        - `automake` for the `aclocal` binary
        - `autoconf` for the `autoreconf` binary
        - `libltdl-dev` which defines the `LT_SYS_SYMBOL_USCORE` macro

    .. note::
        Some notes about libffi version:

            - v3.2.1 it's from year 2014...it's a little outdated and has
              problems with clang (see issue #1525)
            - v3.3-rc0 it was released at april 2018 (it's a pre-release), and
              it lacks some commits that we are interested, specially those
              ones that fixes specific issues for Arm64, you can check those
              commits at (search for commit `8fa8837` and look at the below
              commits): https://github.com/libffi/libffi/commits/master
    """
    name = 'libffi'
    # Version pinned to post `v3.3RC0`
    version = '8fa8837'
    url = 'https://github.com/libffi/libffi/archive/{version}.tar.gz'

    patches = ['remove-version-info.patch']

    built_libraries = {'libffi.so': '.libs'}

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            if not exists('configure'):
                shprint(sh.Command('./autogen.sh'), _env=env)
            shprint(sh.Command('autoreconf'), '-vif', _env=env)
            shprint(sh.Command('./configure'),
                    '--host=' + arch.command_prefix,
                    '--prefix=' + self.get_build_dir(arch.arch),
                    '--disable-builddir',
                    '--enable-shared', _env=env)
            shprint(sh.make, '-j', str(cpu_count()), 'libffi.la', _env=env)

    def get_include_dirs(self, arch):
        return [join(self.get_build_dir(arch.arch), 'include')]


recipe = LibffiRecipe()
