from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from os.path import join


class PillowRecipe(CompiledComponentsPythonRecipe):

    version = '7.0.0'
    url = 'https://github.com/python-pillow/Pillow/archive/{version}.tar.gz'
    site_packages_name = 'Pillow'
    depends = ['png', 'jpeg', 'freetype', 'setuptools']
    patches = [join('patches', 'fix-setup.patch')]

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)

        env['ANDROID_ROOT'] = join(self.ctx.ndk_platform, 'usr')
        ndk_lib_dir = join(self.ctx.ndk_platform, 'usr', 'lib')
        ndk_include_dir = join(self.ctx.ndk_dir, 'sysroot', 'usr', 'include')

        png = self.get_recipe('png', self.ctx)
        png_lib_dir = join(png.get_build_dir(arch.arch), '.libs')
        png_inc_dir = png.get_build_dir(arch)

        jpeg = self.get_recipe('jpeg', self.ctx)
        jpeg_inc_dir = jpeg_lib_dir = jpeg.get_build_dir(arch.arch)

        freetype = self.get_recipe('freetype', self.ctx)
        free_lib_dir = join(freetype.get_build_dir(arch.arch), 'objs', '.libs')
        free_inc_dir = join(freetype.get_build_dir(arch.arch), 'include')

        # harfbuzz is a direct dependency of freetype and we need the proper
        # flags to successfully build the Pillow recipe, so we add them here.
        harfbuzz = self.get_recipe('harfbuzz', self.ctx)
        harf_lib_dir = join(harfbuzz.get_build_dir(arch.arch), 'src', '.libs')
        harf_inc_dir = harfbuzz.get_build_dir(arch.arch)

        env['JPEG_ROOT'] = '{}|{}'.format(jpeg_lib_dir, jpeg_inc_dir)
        env['FREETYPE_ROOT'] = '{}|{}'.format(free_lib_dir, free_inc_dir)
        env['ZLIB_ROOT'] = '{}|{}'.format(ndk_lib_dir, ndk_include_dir)

        cflags = ' -I{}'.format(png_inc_dir)
        cflags += ' -I{} -I{}'.format(harf_inc_dir, join(harf_inc_dir, 'src'))
        cflags += ' -I{}'.format(free_inc_dir)
        cflags += ' -I{}'.format(jpeg_inc_dir)
        cflags += ' -I{}'.format(ndk_include_dir)

        env['LIBS'] = ' -lpng -lfreetype -lharfbuzz -ljpeg -lturbojpeg'

        env['LDFLAGS'] += ' -L{} -L{} -L{} -L{}'.format(
            png_lib_dir, harf_lib_dir, jpeg_lib_dir, ndk_lib_dir)
        if cflags not in env['CFLAGS']:
            env['CFLAGS'] += cflags
        return env


recipe = PillowRecipe()
