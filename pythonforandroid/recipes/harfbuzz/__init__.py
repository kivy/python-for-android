
from pythonforandroid.toolchain import Recipe, shprint, current_directory, ArchARM
from os.path import exists, join, realpath
from os import uname
import glob
import sh


class HarfbuzzRecipe(Recipe):
    version = '0.9.40'
    url = 'http://www.freedesktop.org/software/harfbuzz/release/harfbuzz-{version}.tar.bz2'

    def should_build(self, arch):
        if exists(join(self.get_build_dir(arch.arch), 'src', '.libs', 'libharfbuzz.so')):
            return False
        return True

    def build_arch(self, arch):

        env = self.get_recipe_env(arch)
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch) +
            '-L{}'.format(self.ctx.libs_dir))
        with current_directory(self.get_build_dir(arch.arch)):
            configure = sh.Command('./configure')
            shprint(configure, '--without-icu', '--host=arm-linux=androideabi',
                    '--prefix={}'.format(join(self.ctx.build_dir, 'python-install')),
                    '--without-freetype', '--without-glib', _env=env)
            shprint(sh.make, '-j5', _env=env)

            shprint(sh.cp, '-L', join('src', '.libs', 'libharfbuzz.so'), self.ctx.libs_dir)

recipe = HarfbuzzRecipe()
