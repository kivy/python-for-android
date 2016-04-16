
from pythonforandroid.toolchain import Recipe, shprint
from pythonforandroid.util import current_directory, ensure_dir
from os.path import exists, join
import sh

# NOTE: The libraries, freetype and harfbuzz, are special because they has cyclic dependencies:
# freetype can be build with harfbuzz support and harfbuzz can be build with freetype support.
# So, to correctly build both libraries, first we must build freetype without harfbuzz,
# then we build harfbuzz with freetype support and then we build again the freetype
# library with harfbuzz support. See reference at:
# https://sourceforge.net/projects/freetype/files/freetype2/2.5.3/
class HarfbuzzRecipe(Recipe):
    version = '0.9.40'
    url = 'http://www.freedesktop.org/software/harfbuzz/release/harfbuzz-{version}.tar.bz2'

    def should_build(self, arch):
        if exists(join(self.get_build_dir(arch.arch),
                       'src', '.libs', 'libharfbuzz.a')):
            return False
        return True

    def get_jni_dir(self, arch):
        return join(self.ctx.bootstrap.build_dir, 'jni')

    def get_lib_dir(self, arch):
        if 'pygame' in self.ctx.recipe_build_order:
            return join(self.get_jni_dir(arch), 'harfbuzz', arch.arch)
        return join(self.get_build_dir(arch.arch), 'src', '.libs')

    def build_arch(self, arch):

        env = self.get_recipe_env(arch)
        env['LDFLAGS'] += ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch) + '-L{}'.format(self.ctx.libs_dir))

        with_freetype = 'no'
        if 'freetype' in self.ctx.recipe_build_order:
            # Link with freetype
            with_freetype = 'yes'
            freetype = self.get_recipe('freetype', self.ctx)
            freetype_install = join(freetype.get_build_dir(arch.arch), 'install')
            env['CFLAGS'] = ' '.join([env['CFLAGS'], '-I{}/include/freetype2'.format(freetype_install),
                                      '-L{}/lib'.format(freetype_install), '-lfreetype'])

        with current_directory(self.get_build_dir(arch.arch)):
            configure = sh.Command('./configure')
            shprint(configure, '--without-icu', '--host=arm-linux=androideabi',
                    '--prefix={}'.format(join(self.ctx.build_dir, 'python-install')),
                    '--with-freetype={}'.format(with_freetype), '--without-glib',
                    '--disable-shared', _env=env)
            shprint(sh.make, '-j5', _env=env)

            shprint(sh.cp, '-L', join('src', '.libs', 'libharfbuzz.a'), self.ctx.libs_dir)

        if 'freetype' in self.ctx.recipe_build_order:
            # Rebuild freetype with harfbuzz support
            freetype.build_arch(arch, with_harfbuzz=True)

recipe = HarfbuzzRecipe()
