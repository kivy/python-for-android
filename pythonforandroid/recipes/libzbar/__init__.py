import os
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory
from pythonforandroid.logger import shprint
from multiprocessing import cpu_count
import sh


class LibZBarRecipe(Recipe):

    version = '0.23.1'

    url = 'https://github.com/mchehab/zbar/archive/{version}.tar.gz'
    sha256sum = '297439f8859089d2248f55ab95b2a90bba35687975365385c87364c77fdb19f3'

    depends = ['libiconv']

    patches = ['remove-version-info.patch']

    built_libraries = {'libzbar.so': 'zbar/.libs'}

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        libiconv = self.get_recipe('libiconv', self.ctx)
        libiconv_dir = libiconv.get_build_dir(arch.arch)
        env['CFLAGS'] += ' -I' + os.path.join(libiconv_dir, 'include')
        env['LIBS'] = env.get('LIBS', '') + ' -landroid -liconv'
        return env

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.Command('autoreconf'), '-vif', _env=env)
            shprint(
                sh.Command('./configure'),
                '--host=' + arch.command_prefix,
                '--target=' + arch.toolchain_prefix,
                '--prefix=' + self.ctx.get_python_install_dir(),
                # Python bindings are compiled in a separated recipe
                '--with-python=no',
                '--with-gtk=no',
                '--with-qt=no',
                '--with-x=no',
                '--with-jpeg=no',
                '--with-imagemagick=no',
                '--with-dbus=no',
                '--enable-pthread=no',
                '--enable-video=no',
                '--enable-shared=yes',
                '--enable-static=no',
                _env=env)
            shprint(sh.make, '-j' + str(cpu_count()), _env=env)


recipe = LibZBarRecipe()
