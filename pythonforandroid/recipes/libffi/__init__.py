from os.path import exists, join
from multiprocessing import cpu_count
from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory, ensure_dir
import sh


class LibffiRecipe(Recipe):
    """
    Requires additional system dependencies on Ubuntu:
        - `automake` for the `aclocal` binary
        - `autoconf` for the `autoreconf` binary
        - `libltdl-dev` which defines the `LT_SYS_SYMBOL_USCORE` macro
    """
    name = 'libffi'
    version = '3.2.1'
    url = 'https://github.com/libffi/libffi/archive/v{version}.tar.gz'

    patches = ['remove-version-info.patch',
               # This patch below is already included into libffi's master
               # branch and included in the pre-release 3.3rc0...so we should
               # remove this when we update the version number for libffi
               'fix-includedir.patch']

    def should_build(self, arch):
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libffi.so'))

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

            host_build = self.get_build_dir(arch.arch)
            ensure_dir(self.ctx.get_libs_dir(arch.arch))
            shprint(sh.cp,
                    join(host_build, '.libs', 'libffi.so'),
                    self.ctx.get_libs_dir(arch.arch))

    def get_include_dirs(self, arch):
        return [join(self.get_build_dir(arch.arch), 'include')]


recipe = LibffiRecipe()
