from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.toolchain import shprint
from os.path import join, dirname
import sh


class PillowRecipe(CompiledComponentsPythonRecipe):

    version = '5.2.0'
    url = 'https://github.com/python-pillow/Pillow/archive/{version}.tar.gz'
    site_packages_name = 'Pillow'
    depends = [
        ('python2', 'python3crystax'),
        'png',
        'jpeg',
        'freetype',
        'setuptools'
    ]
    patches = [
        join('patches', 'fix-docstring.patch'),
        join('patches', 'fix-setup.patch')
    ]

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None):
        env = super(PillowRecipe, self).get_recipe_env(arch)
        py_ver = self.ctx.python_recipe.version[0:3]

        ndk_dir = self.ctx.ndk_platform
        ndk_lib_dir = join(ndk_dir, 'usr', 'lib')
        ndk_include_dir = (
            join(self.ctx.ndk_dir, 'sysroot', 'usr', 'include')
            if py_ver == '2.7' else join(ndk_dir, 'usr', 'include'))

        png = self.get_recipe('png', self.ctx)
        png_lib_dir = png.get_lib_dir(arch)
        png_jni_dir = png.get_jni_dir(arch)

        jpeg = self.get_recipe('jpeg', self.ctx)
        jpeg_lib_dir = jpeg.get_lib_dir(arch)
        jpeg_jni_dir = jpeg.get_jni_dir(arch)

        env['JPEG_ROOT'] = '{}|{}'.format(jpeg_lib_dir, jpeg_jni_dir)
        env['ZLIB_ROOT'] = '{}|{}'.format(ndk_lib_dir, ndk_include_dir)

        cflags = ' -nostdinc'
        cflags += ' -I{} -L{}'.format(png_jni_dir, png_lib_dir)
        cflags += ' -I{} -L{}'.format(jpeg_jni_dir, jpeg_lib_dir)
        cflags += ' -I{} -L{}'.format(ndk_include_dir, ndk_lib_dir)

        gcc_lib = shprint(
            sh.gcc, '-print-libgcc-file-name').stdout.decode('utf-8').split('\n')[0]
        gcc_include = join(dirname(gcc_lib), 'include')
        cflags += ' -I{}'.format(gcc_include)

        if self.ctx.ndk == 'crystax':
            py_inc_dir = join(
                self.ctx.ndk_dir, 'sources', 'python', py_ver, 'include', 'python')
            py_lib_dir = join(
                self.ctx.ndk_dir, 'sources', 'python', py_ver, 'libs', arch.arch)
            cflags += ' -I{}'.format(py_inc_dir)
            env['LDFLAGS'] += ' -L{} -lpython{}m'.format(py_lib_dir, py_ver)

        env['LDFLAGS'] += ' {} -L{}'.format(env['CFLAGS'], self.ctx.libs_dir)
        if cflags not in env['CFLAGS']:
            env['CFLAGS'] += cflags
        env['LDSHARED'] = '{} {}'.format(
            env['CC'],
            '-pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions')
        return env


recipe = PillowRecipe()
