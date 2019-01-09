from pythonforandroid.toolchain import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from os.path import exists, join
import sh


class HarfbuzzRecipe(Recipe):
    version = '0.9.40'
    url = 'http://www.freedesktop.org/software/harfbuzz/release/harfbuzz-{version}.tar.bz2'  # noqa

    def should_build(self, arch):
        if exists(join(self.get_build_dir(arch.arch),
                       'src', '.libs', 'libharfbuzz.a')):
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
                    '--prefix={}'.format(
                        join(self.ctx.build_dir, 'python-install')),
                    '--without-freetype',
                    '--without-glib',
                    '--disable-shared',
                    _env=env)
            shprint(sh.make, '-j5', _env=env)

            shprint(sh.cp, '-L', join('src', '.libs', 'libharfbuzz.a'),
                    self.ctx.libs_dir)


recipe = HarfbuzzRecipe()
