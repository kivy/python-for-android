import sh

from multiprocessing import cpu_count
from os.path import exists, join

from pythonforandroid.archs import Arch
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory


class LibLzmaRecipe(Recipe):

    version = '5.2.4'
    url = 'https://tukaani.org/xz/xz-{version}.tar.gz'
    built_libraries = {'liblzma.so': 'p4a_install/lib'}

    def build_arch(self, arch: Arch) -> None:
        env = self.get_recipe_env(arch)
        install_dir = join(self.get_build_dir(arch.arch), 'p4a_install')
        with current_directory(self.get_build_dir(arch.arch)):
            if not exists('configure'):
                shprint(sh.Command('./autogen.sh'), _env=env)
            shprint(sh.Command('autoreconf'), '-vif', _env=env)
            shprint(sh.Command('./configure'),
                    '--host=' + arch.command_prefix,
                    '--prefix=' + install_dir,
                    '--disable-builddir',
                    '--disable-static',
                    '--enable-shared',

                    '--disable-xz',
                    '--disable-xzdec',
                    '--disable-lzmadec',
                    '--disable-lzmainfo',
                    '--disable-scripts',
                    '--disable-doc',

                    _env=env)
            shprint(
                sh.make, '-j', str(cpu_count()),
                _env=env
            )

            shprint(sh.make, 'install', _env=env)

    def get_library_includes(self, arch: Arch) -> str:
        """
        Returns a string with the appropriate `-I<lib directory>` to link
        with the lzma lib. This string is usually added to the environment
        variable `CPPFLAGS`.
        """
        return " -I" + join(
            self.get_build_dir(arch.arch), 'p4a_install', 'include',
        )

    def get_library_ldflags(self, arch: Arch) -> str:
        """
        Returns a string with the appropriate `-L<lib directory>` to link
        with the lzma lib. This string is usually added to the environment
        variable `LDFLAGS`.
        """
        return " -L" + join(
            self.get_build_dir(arch.arch), self.built_libraries['liblzma.so'],
        )

    @staticmethod
    def get_library_libs_flag() -> str:
        """
        Returns a string with the appropriate `-l<lib>` flags to link with
        the lzma lib. This string is usually added to the environment
        variable `LIBS`.
        """
        return " -llzma"


recipe = LibLzmaRecipe()
