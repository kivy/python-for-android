from pythonforandroid.toolchain import shprint
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.logger import info
from os.path import join, exists
import sh


class PILRecipe(CompiledComponentsPythonRecipe):
    name = 'pil'
    version = '3.1.0'
    url = 'https://pypi.python.org/packages/source/P/Pillow/Pillow-{version}.tar.gz'
    depends = ['incremental', 'setuptools', ('python2', 'python3'), 'png', 'jpeg', 'freetype']
    call_hostpython_via_targetpython = False
    site_packages_name = 'PIL'
    patches = ['disable-tk.patch',
               'fix-directories.patch']

    def get_recipe_env(self, arch=None):
        # The python's headers/linking should be placed into recipe.py file...
        # and should be removed at some point, details in:
        # https://github.com/kivy/python-for-android/pull/793/files
        env = super(PILRecipe, self).get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -lpython2.7'

        # Set linker to use the correct gcc
        env['LDSHARED'] = env['CC'] + ' -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions'

        # png flags
        r = self.get_recipe('png', self.ctx)
        png_lib_dir = r.get_lib_dir(arch)
        png_inc_dir = join(r.get_build_dir(arch.arch), 'jni')
        cflags = ' -I{} -L{}'.format(png_inc_dir, png_lib_dir)

        # jpeg flags
        r = self.get_recipe('jpeg', self.ctx)
        jpeg_lib_dir = r.get_lib_dir(arch)
        jpeg_jni_dir = r.get_jni_dir(arch)
        cflags += ' -I{} -I{} -I{} -L{}'.format(
            jpeg_jni_dir, join(jpeg_jni_dir, 'android'),
            join(jpeg_jni_dir, 'simd'), jpeg_lib_dir)

        # freetype flags
        r = self.get_recipe('freetype', self.ctx)
        env['FREETYPE_VERSION'] = r.version
        free_lib_dir = join(r.get_build_dir(arch.arch), 'objs', '.libs')
        free_inc_dir = join(r.get_build_dir(arch.arch), 'include')
        cflags += ' -I{} -L{}'.format(free_inc_dir, free_lib_dir)
        env['LDFLAGS'] += ' -L{} -lfreetype{}'.format(
            free_lib_dir, '')
        if 'harfbuzz' in self.ctx.recipe_build_order:
            r = self.get_recipe('harfbuzz', self.ctx)
            harf_lib_dir = join(r.get_build_dir(arch.arch), 'src', '.libs')
            harf_inc_dir = r.get_build_dir(arch.arch)
            cflags += ' -I{} -I{} -L{}'.format(
                harf_inc_dir, join(harf_inc_dir, 'src'),
                harf_lib_dir)
            env['LDFLAGS'] += ' -L{} -lharfbuzz{}'.format(
                harf_lib_dir, '')
        # Patch freetype headers to be found by pil
        freetype_link = join(free_inc_dir, 'freetype')
        if not exists(freetype_link):
            shprint(sh.ln, '-s', join(free_inc_dir), freetype_link)

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
