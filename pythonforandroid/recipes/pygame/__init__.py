
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.util import ensure_dir
from pythonforandroid.logger import debug, shprint
from os.path import exists, join
import sh

class PygameRecipe(CompiledComponentsPythonRecipe):
    name = 'pygame'
    version = '1.9.1'
    url = 'http://pygame.org/ftp/pygame-{version}release.tar.gz'

    depends = ['python2', 'sdl']
    conflicts = ['sdl2']

    patches = ['patches/fix-surface-access.patch',
               'patches/fix-array-surface.patch',
               'patches/fix-sdl-spam-log.patch']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None):
        env = super(PygameRecipe, self).get_recipe_env(arch)

        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        # SET LINKER TO USE THE CORRECT GCC
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -lpython2.7'

        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch))
        env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')
        env['LIBLINK'] = 'NOTNONE'
        env['NDKPLATFORM'] = self.ctx.ndk_platform

        # PATCH FREETYPE HEADERS TO BE FOUND BY PYGAME
        freetype_inc_dir = join(self.ctx.bootstrap_build_dir, 'jni', 'freetype', 'include')
        if not exists(join(freetype_inc_dir, 'freetype')):
            shprint(sh.ln, '-s', freetype_inc_dir,
                    join(freetype_inc_dir, 'freetype'))

        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/png -I{jni_path}/jpeg -I{jni_path}/freetype/include'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/sdl/include -I{jni_path}/sdl_mixer'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        env['CFLAGS'] = env['CFLAGS'] + ' -I{jni_path}/sdl_ttf -I{jni_path}/sdl_image'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        debug('pygame cflags', env['CFLAGS'])

        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{libs_path} -L{src_path}/obj/local/{arch} -lm -lz'.format(
            libs_path=self.ctx.libs_dir, src_path=self.ctx.bootstrap.build_dir, arch=env['ARCH'])

        env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')
        # Every recipe uses its own liblink path, object files are collected and biglinked later
        liblink_path = join(self.get_build_container_dir(arch.arch), 'objects_{}'.format(self.name))
        env['LIBLINK_PATH'] = liblink_path
        ensure_dir(liblink_path)
        return env

    def prebuild_arch(self, arch):
        if self.is_patched(arch):
            return
        shprint(sh.cp, join(self.get_recipe_dir(), 'Setup'),
                join(self.get_build_dir(arch.arch), 'Setup'))


recipe = PygameRecipe()
