
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.util import ensure_dir
from pythonforandroid.logger import debug, shprint
from os.path import join
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

        env['LDFLAGS'] += ' -L{}'.format(self.ctx.get_libs_dir(arch.arch))
        env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')
        env['LIBLINK'] = 'NOTNONE'
        env['NDKPLATFORM'] = self.ctx.ndk_platform

        # PNG FLAGS
        png = self.get_recipe('png', self.ctx)
        png_lib_dir = png.get_lib_dir(arch)
        png_inc_dir = png.get_include_dir(arch)
        env['CFLAGS'] += ' -I{}'.format(png_inc_dir)
        env['LDFLAGS'] += ' -L{} -lpng'.format(png_lib_dir)

        # JPEG TURBO FLAGS
        jpeg = self.get_recipe('jpeg', self.ctx)
        jpeg_lib_dir = jpeg.get_lib_dir(arch)
        jpeg_jni_dir = jpeg.get_jni_dir(arch)
        env['CFLAGS'] += ' -I{} -I{} -I{}'.format(
            jpeg_jni_dir, join(jpeg_jni_dir, 'android'),
            join(jpeg_jni_dir, 'simd'))
        env['LDFLAGS'] += ' -L{} -lsimd -ljpeg'.format(jpeg_lib_dir)

        # FREETYPE FLAGS
        free = self.get_recipe('freetype', self.ctx)
        free_lib_dir = free.get_lib_dir(arch)
        free_inc_dir = join(free.get_build_dir(arch.arch), 'include')
        env['CFLAGS'] += ' -I{} -L{}'.format(free_inc_dir, free_lib_dir)
        if 'harfbuzz' in self.ctx.recipe_build_order:
            free_install = join(free.get_build_dir(arch.arch), 'install')
            harf = self.get_recipe('harfbuzz', self.ctx)
            harf_lib_dir = harf.get_lib_dir(arch)
            harf_inc_dir = harf.get_build_dir(arch.arch)
            env['CFLAGS'] += ' -I{} -I{} -I{} -L{}'.format(
                harf_inc_dir, join(harf_inc_dir, 'src'),
                join(free_install, 'include'), harf_lib_dir)
            env['LDFLAGS'] += ' -L{} -lharfbuzz'.format(harf_lib_dir)

        env['CFLAGS'] += ' -I{jni_path}/sdl/include -I{jni_path}/sdl_mixer'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        env['CFLAGS'] += ' -I{jni_path}/sdl_ttf -I{jni_path}/sdl_image'.format(
            jni_path=join(self.ctx.bootstrap.build_dir, 'jni'))
        debug('pygame cflags', env['CFLAGS'])

        env['LDFLAGS'] += ' -L{src_path}/obj/local/{arch} -lm -lz'.format(
            src_path=self.ctx.bootstrap.build_dir, arch=env['ARCH'])

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
