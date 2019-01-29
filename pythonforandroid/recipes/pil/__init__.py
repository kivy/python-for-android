from os.path import join, exists
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.toolchain import shprint
import sh


class PILRecipe(CompiledComponentsPythonRecipe):
    name = 'pil'
    version = '1.1.7'
    url = 'http://effbot.org/downloads/Imaging-{version}.tar.gz'
    depends = ['png', 'jpeg', 'setuptools']
    opt_depends = ['freetype']
    site_packages_name = 'PIL'

    patches = ['disable-tk.patch',
               'fix-directories.patch']

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(PILRecipe, self).get_recipe_env(arch, with_flags_in_cc)

        env['PYTHON_INCLUDE_ROOT'] = self.ctx.python_recipe.include_root(arch.arch)
        env['PYTHON_LINK_ROOT'] = self.ctx.python_recipe.link_root(arch.arch)

        ndk_lib_dir = join(self.ctx.ndk_platform, 'usr', 'lib')
        ndk_include_dir = join(self.ctx.ndk_dir, 'sysroot', 'usr', 'include')

        png = self.get_recipe('png', self.ctx)
        png_lib_dir = png.get_lib_dir(arch)
        png_jni_dir = png.get_jni_dir(arch)

        jpeg = self.get_recipe('jpeg', self.ctx)
        jpeg_inc_dir = jpeg_lib_dir = jpeg.get_build_dir(arch.arch)

        if 'freetype' in self.ctx.recipe_build_order:
            freetype = self.get_recipe('freetype', self.ctx)
            free_lib_dir = join(freetype.get_build_dir(arch.arch), 'objs', '.libs')
            free_inc_dir = join(freetype.get_build_dir(arch.arch), 'include')
            # hack freetype to be found by pil
            freetype_link = join(free_inc_dir, 'freetype')
            if not exists(freetype_link):
                shprint(sh.ln, '-s', join(free_inc_dir), freetype_link)

            harfbuzz = self.get_recipe('harfbuzz', self.ctx)
            harf_lib_dir = join(harfbuzz.get_build_dir(arch.arch), 'src', '.libs')
            harf_inc_dir = harfbuzz.get_build_dir(arch.arch)

            env['FREETYPE_ROOT'] = '{}|{}'.format(free_lib_dir, free_inc_dir)

        env['JPEG_ROOT'] = '{}|{}'.format(jpeg_lib_dir, jpeg_inc_dir)
        env['ZLIB_ROOT'] = '{}|{}'.format(ndk_lib_dir, ndk_include_dir)

        cflags = ' -std=c99'
        cflags += ' -I{}'.format(png_jni_dir)
        if 'freetype' in self.ctx.recipe_build_order:
            cflags += ' -I{} -I{}'.format(harf_inc_dir, join(harf_inc_dir, 'src'))
            cflags += ' -I{}'.format(free_inc_dir)
        cflags += ' -I{}'.format(jpeg_inc_dir)
        cflags += ' -I{}'.format(ndk_include_dir)

        py_v = self.ctx.python_recipe.major_minor_version_string
        if py_v[0] == '3':
            py_v += 'm'

        env['LIBS'] = ' -lpython{version} -lpng'.format(version=py_v)
        if 'freetype' in self.ctx.recipe_build_order:
            env['LIBS'] += ' -lfreetype -lharfbuzz'
        env['LIBS'] += ' -ljpeg -lturbojpeg'

        env['LDFLAGS'] += ' -L{} -L{}'.format(env['PYTHON_LINK_ROOT'], png_lib_dir)
        if 'freetype' in self.ctx.recipe_build_order:
            env['LDFLAGS'] += ' -L{} -L{}'.format(harf_lib_dir, free_lib_dir)
        env['LDFLAGS'] += ' -L{} -L{}'.format(jpeg_lib_dir, ndk_lib_dir)

        if cflags not in env['CFLAGS']:
            env['CFLAGS'] += cflags
        return env


recipe = PILRecipe()
