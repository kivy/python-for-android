
from pythonforandroid.toolchain import Recipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.util import current_directory, ensure_dir
from os.path import exists, join, realpath
import sh

# NOTE: The libraries, freetype and harfbuzz, are special because they has cyclic dependencies:
# freetype can be build with harfbuzz support and harfbuzz can be build with freetype support.
# So, to correctly build both libraries, first we must build freetype without harfbuzz,
# then we build harfbuzz with freetype support and then we build again the freetype
# library with harfbuzz support. See reference at:
# https://sourceforge.net/projects/freetype/files/freetype2/2.5.3/
class FreetypeRecipe(Recipe):
    version = '2.5.5'
    url = 'http://download.savannah.gnu.org/releases/freetype/freetype-{version}.tar.gz'
    opt_depends = ['harfbuzz']

    def should_build(self, arch):
        if exists(join(self.get_build_dir(arch.arch), 'objs', '.libs', 'libfreetype.a')):
            return False
        return True

    def get_jni_dir(self, arch):
        return join(self.ctx.bootstrap.build_dir, 'jni')

    def get_lib_dir(self, arch):
        return join(self.get_build_dir(arch.arch), 'objs', '.libs')

    def build_arch(self, arch, with_harfbuzz=False):
        env = self.get_recipe_env(arch)
        use_harfbuzz = False
        prefix_path = realpath('.')
        if 'harfbuzz' in self.ctx.recipe_build_order:
            use_harfbuzz = True
            if not with_harfbuzz:
                info('\t - This is the first Build of freetype (without harfbuzz)')
                prefix_path = join(self.get_build_dir(arch.arch), 'install')

        if with_harfbuzz:
            # Is the second build, now we link with harfbuzz
            info('\t - This is the second Build of freetype: enabling harfbuzz support ...')
            harfbuzz_build = Recipe.get_recipe('harfbuzz', self.ctx).get_build_dir(arch.arch)
            freetype_install = join(self.get_build_dir(arch.arch), 'install')
            env['CFLAGS'] = ' '.join(
                [env['CFLAGS'], '-I{harfbuzz}'.format(harfbuzz=harfbuzz_build),
                 '-I{harfbuzz}/src'.format(harfbuzz=harfbuzz_build),
                 '-I{freetype}/include/freetype2'.format(freetype=freetype_install),
                 '-L{freetype}/lib -lfreetype'.format(freetype=freetype_install)])
            env['LDFLAGS'] = ' '.join(['-L{freetype}/lib -lfreetype'.format(freetype=freetype_install)])

            env['HARFBUZZ_CFLAGS'] = '-I{harfbuzz} -I{harfbuzz}/src'.format(harfbuzz=harfbuzz_build)
            env['HARFBUZZ_LIBS'] = '-L{freetype}/lib -lfreetype ' \
                                   '-L{harfbuzz}/src/.libs -lharfbuzz'.format(
                freetype=freetype_install, harfbuzz=harfbuzz_build)

        # Build freetype library
        with current_directory(self.get_build_dir(arch.arch)):
            configure = sh.Command('./configure')
            shprint(configure, '--host=arm-linux-androideabi',
                    '--prefix={}'.format(prefix_path),
                    '--without-zlib', '--with-png=no',
                    '--disable-shared', _env=env)
            shprint(sh.make, '-j5', _env=env)

            if not with_harfbuzz and use_harfbuzz:
                # Is first build, install the compiled lib, and clean build env
                shprint(sh.make, 'install', _env=env)
                shprint(sh.make, 'distclean', _env=env)
            else:
                # This is the second build (or the first if harfbuzz not enabled),
                # now we copy definitive libs to libs collection. Be sure to link
                # your recipes to the definitive library, located at: objs/.libs
                ensure_dir(join(self.ctx.libs_dir, arch.arch))
                shprint(sh.cp, 'objs/.libs/libfreetype.a', self.ctx.libs_dir)


recipe = FreetypeRecipe()
