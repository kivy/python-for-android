from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.logger import info
from os.path import join

class PILRecipe(CompiledComponentsPythonRecipe):
    name = 'pil'
    version = '3.1.0'
    url = 'https://pypi.python.org/packages/source/P/Pillow/Pillow-{version}.tar.gz'
    depends = ['setuptools', ('python2', 'python3'), 'png', 'jpeg', 'freetype']
    call_hostpython_via_targetpython = False
    site_packages_name = 'PIL'
    patches = ['disable-tk.patch',
               'fix-directories.patch']

    def get_recipe_env(self, arch=None):
        env = super(PILRecipe, self).get_recipe_env(arch)
        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'

        # PNG FLAGS
        png = self.get_recipe('png', self.ctx)
        png_lib_dir = png.get_lib_dir(arch)
        png_inc_dir = png.get_include_dir(arch)
        cflags = ' -I{} -L{}'.format(png_inc_dir, png_lib_dir)

        # JPEG TURBO FLAGS
        jpeg = self.get_recipe('jpeg', self.ctx)
        jpeg_lib_dir = jpeg.get_lib_dir(arch)
        jpeg_jni_dir = jpeg.get_jni_dir(arch)
        cflags += ' -I{} -I{} -I{} -L{}'.format(
            jpeg_jni_dir, join(jpeg_jni_dir, 'android'),
            join(jpeg_jni_dir, 'simd'), jpeg_lib_dir)

        # FREETYPE FLAGS
        free = self.get_recipe('freetype', self.ctx)
        free_lib_dir = free.get_lib_dir(arch)
        free_inc_dir = join(free.get_build_dir(arch.arch), 'include')
        cflags = ' -I{} -L{}'.format(free_inc_dir, free_lib_dir)
        if 'harfbuzz' in self.ctx.recipe_build_order:
            free_install = join(free.get_build_dir(arch.arch), 'install')
            harf = self.get_recipe('harfbuzz', self.ctx)
            harf_lib_dir = harf.get_lib_dir(arch)
            harf_inc_dir = harf.get_build_dir(arch.arch)
            cflags += ' -I{} -I{} -I{} -L{}'.format(
                harf_inc_dir, join(harf_inc_dir, 'src'),
                join(free_install, 'include'), harf_lib_dir)

        env['JPEG_ROOT'] = '{}|{}'.format(jpeg_lib_dir, jpeg_jni_dir)
        env['FREETYPE_ROOT'] = '{}|{}'.format(free_lib_dir, free_inc_dir)
        info('JPEG_ROOT: {}'.format(env['JPEG_ROOT']))
        info('FREETYPE_ROOT: {}'.format(env['FREETYPE_ROOT']))

        env['CFLAGS'] += cflags
        env['CXXFLAGS'] += cflags
        env['CC'] += cflags
        env['CXX'] += cflags

        ndk_dir = self.ctx.ndk_platform
        ndk_lib_dir = join(ndk_dir, 'usr', 'lib')
        ndk_include_dir = join(ndk_dir, 'usr', 'include')
        env['ZLIB_ROOT'] = '{}|{}'.format(ndk_lib_dir, ndk_include_dir)

        return env

recipe = PILRecipe()
