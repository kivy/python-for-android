import sh

from multiprocessing import cpu_count

from pythonforandroid.archs import Arch
from pythonforandroid.logger import shprint
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory


class LibBz2Recipe(Recipe):

    version = "1.0.8"
    url = "https://sourceware.org/pub/bzip2/bzip2-{version}.tar.gz"
    built_libraries = {"libbz2.so": ""}
    patches = ["lib_android.patch"]

    def build_arch(self, arch: Arch) -> None:
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(
                sh.make,
                "-j",
                str(cpu_count()),
                f'CC={env["CC"]}',
                "-f",
                "Makefile-libbz2_so",
                _env=env,
            )

    def get_library_includes(self, arch: Arch) -> str:
        """
        Returns a string with the appropriate `-I<lib directory>` to link
        with the bz2 lib. This string is usually added to the environment
        variable `CPPFLAGS`.
        """
        return " -I" + self.get_build_dir(arch.arch)

    def get_library_ldflags(self, arch: Arch) -> str:
        """
        Returns a string with the appropriate `-L<lib directory>` to link
        with the bz2 lib. This string is usually added to the environment
        variable `LDFLAGS`.
        """
        return " -L" + self.get_build_dir(arch.arch)

    @staticmethod
    def get_library_libs_flag() -> str:
        """
        Returns a string with the appropriate `-l<lib>` flags to link with
        the bz2 lib. This string is usually added to the environment
        variable `LIBS`.
        """
        return " -lbz2"


recipe = LibBz2Recipe()
