
from pythonforandroid.toolchain import Recipe, shprint, current_directory, ArchARM
from os.path import exists, join, realpath
from os import uname
import glob
import sh

class FreetypeRecipe(Recipe):

    version = '2.5.5'
    url = 'http://download.savannah.gnu.org/releases/freetype/freetype-{version}.tar.gz'

    depends = ['harfbuzz']

    def should_build(self, arch):
        if exists(join(self.get_build_dir(arch.arch), 'objs', '.libs', 'libfreetype.so')):
            return False
        return True

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        harfbuzz_recipe = Recipe.get_recipe('harfbuzz', self.ctx)
        env['LDFLAGS'] = ' '.join(
            [env['LDFLAGS'],
             '-L{}'.format(join(harfbuzz_recipe.get_build_dir(arch.arch), 'src', '.libs'))])

        with current_directory(self.get_build_dir(arch.arch)):
            configure = sh.Command('./configure')
            shprint(configure, '--host=arm-linux-androideabi',
                    '--prefix={}'.format(realpath('.')),
                    '--without-zlib', '--with-png=no', '--enable-shared',
                    _env=env)
            shprint(sh.make, '-j5', _env=env)

            shprint(sh.cp, 'objs/.libs/libfreetype.so', self.ctx.libs_dir)


recipe = FreetypeRecipe()
