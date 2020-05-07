from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from multiprocessing import cpu_count
from os.path import join
import sh


class HarfbuzzRecipe(Recipe):
    """The harfbuzz library it's special, because has cyclic dependencies with
    freetype library, so freetype can be build with harfbuzz support, and
    harfbuzz can be build with freetype support. This complicates the build of
    both recipes because in order to get the full set we need to compile those
    recipes several times:
        - build freetype without harfbuzz
        - build harfbuzz with freetype
        - build freetype with harfbuzz support

    .. seealso::
        https://sourceforge.net/projects/freetype/files/freetype2/2.5.3/
    """

    version = '2.6.4'
    url = 'http://www.freedesktop.org/software/harfbuzz/release/harfbuzz-{version}.tar.xz'  # noqa
    opt_depends = ['freetype']
    built_libraries = {'libharfbuzz.so': 'src/.libs'}

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)
        if 'freetype' in self.ctx.recipe_build_order:
            freetype = self.get_recipe('freetype', self.ctx)
            freetype_install = join(
                freetype.get_build_dir(arch.arch), 'install'
            )
            # Explicitly tell harfbuzz's configure script that we want to
            # use our freetype library or it won't be correctly detected
            env['FREETYPE_CFLAGS'] = '-I{}/include/freetype2'.format(
                freetype_install
            )
            env['FREETYPE_LIBS'] = ' '.join(
                ['-L{}/lib'.format(freetype_install), '-lfreetype']
            )
        return env

    def build_arch(self, arch):

        env = self.get_recipe_env(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            configure = sh.Command('./configure')
            shprint(
                configure,
                '--host={}'.format(arch.command_prefix),
                '--prefix={}'.format(self.get_build_dir(arch.arch)),
                '--with-freetype={}'.format(
                    'yes'
                    if 'freetype' in self.ctx.recipe_build_order
                    else 'no'
                ),
                '--with-icu=no',
                '--with-cairo=no',
                '--with-fontconfig=no',
                '--with-glib=no',
                _env=env,
            )
            shprint(sh.make, '-j', str(cpu_count()), _env=env)

        if 'freetype' in self.ctx.recipe_build_order:
            # Rebuild/install freetype with harfbuzz support
            freetype = self.get_recipe('freetype', self.ctx)
            freetype.build_arch(arch, with_harfbuzz=True)
            freetype.install_libraries(arch)


recipe = HarfbuzzRecipe()
