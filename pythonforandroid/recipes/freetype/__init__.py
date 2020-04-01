from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.util import current_directory
from os.path import join, exists
from multiprocessing import cpu_count
import sh


class FreetypeRecipe(Recipe):
    """The freetype library it's special, because has cyclic dependencies with
    harfbuzz library, so freetype can be build with harfbuzz support, and
    harfbuzz can be build with freetype support. This complicates the build of
    both recipes because in order to get the full set we need to compile those
    recipes several times:
        - build freetype without harfbuzz
        - build harfbuzz with freetype
        - build freetype with harfbuzz support

    .. note::
        To build freetype with harfbuzz support you must add `harfbuzz` to your
        requirements, otherwise freetype will be build without harfbuzz

    .. seealso::
        https://sourceforge.net/projects/freetype/files/freetype2/2.5.3/
    """

    version = '2.10.1'
    url = 'http://download.savannah.gnu.org/releases/freetype/freetype-{version}.tar.gz'  # noqa
    built_libraries = {'libfreetype.so': 'objs/.libs'}

    def get_recipe_env(self, arch=None, with_harfbuzz=False):
        env = super().get_recipe_env(arch)
        if with_harfbuzz:
            harfbuzz_build = self.get_recipe(
                'harfbuzz', self.ctx
            ).get_build_dir(arch.arch)
            freetype_install = join(self.get_build_dir(arch.arch), 'install')

            env['HARFBUZZ_CFLAGS'] = '-I{harfbuzz} -I{harfbuzz}/src'.format(
                harfbuzz=harfbuzz_build
            )
            env['HARFBUZZ_LIBS'] = (
                '-L{freetype}/lib -lfreetype '
                '-L{harfbuzz}/src/.libs -lharfbuzz'.format(
                    freetype=freetype_install, harfbuzz=harfbuzz_build
                )
            )

        # android's zlib support
        zlib_lib_path = join(self.ctx.ndk_platform, 'usr', 'lib')
        zlib_includes = join(self.ctx.ndk_dir, 'sysroot', 'usr', 'include')

        def add_flag_if_not_added(flag, env_key):
            if flag not in env[env_key]:
                env[env_key] += flag

        add_flag_if_not_added(' -I' + zlib_includes, 'CFLAGS')
        add_flag_if_not_added(' -L' + zlib_lib_path, 'LDFLAGS')
        add_flag_if_not_added(' -lz', 'LDLIBS')

        return env

    def build_arch(self, arch, with_harfbuzz=False):
        env = self.get_recipe_env(arch, with_harfbuzz=with_harfbuzz)

        harfbuzz_in_recipes = 'harfbuzz' in self.ctx.recipe_build_order
        prefix_path = self.get_build_dir(arch.arch)
        if harfbuzz_in_recipes and not with_harfbuzz:
            # This is the first time we build freetype and we modify `prefix`,
            # because we will install the compiled library so later we can
            # build harfbuzz (with freetype support) using this freetype
            # installation
            prefix_path = join(prefix_path, 'install')

        # Configure freetype library
        config_args = {
            '--host={}'.format(arch.command_prefix),
            '--prefix={}'.format(prefix_path),
            '--without-bzip2',
            '--with-png=no',
        }
        if not harfbuzz_in_recipes:
            info('Build freetype (without harfbuzz)')
            config_args = config_args.union(
                {'--disable-static',
                 '--enable-shared',
                 '--with-harfbuzz=no',
                 '--with-zlib=yes',
                 }
            )
        elif not with_harfbuzz:
            info('Build freetype for First time (without harfbuzz)')
            # This time we will build our freetype library as static because we
            # want that the harfbuzz library to have the necessary freetype
            # symbols/functions, so we avoid to have two freetype shared
            # libraries which will be confusing and harder to link with them
            config_args = config_args.union(
                {'--disable-shared', '--with-harfbuzz=no', '--with-zlib=no'}
            )
        else:
            info('Build freetype for Second time (with harfbuzz)')
            config_args = config_args.union(
                {'--disable-static',
                 '--enable-shared',
                 '--with-harfbuzz=yes',
                 '--with-zlib=yes',
                 }
            )
        info('Configure args are:\n\t-{}'.format('\n\t-'.join(config_args)))

        # Build freetype library
        with current_directory(self.get_build_dir(arch.arch)):
            configure = sh.Command('./configure')
            shprint(configure, *config_args, _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)

            if not with_harfbuzz and harfbuzz_in_recipes:
                info('Installing freetype (first time build without harfbuzz)')
                # First build, install the compiled lib, and clean build env
                shprint(sh.make, 'install', _env=env)
                shprint(sh.make, 'distclean', _env=env)

    def install_libraries(self, arch):
        # This library it's special because the first time we built it may not
        # generate the expected library, because it can depend on harfbuzz, so
        # we will make sure to only install it when the library exists
        if not exists(list(self.get_libraries(arch))[0]):
            return
        self.install_libs(arch, *self.get_libraries(arch))


recipe = FreetypeRecipe()
