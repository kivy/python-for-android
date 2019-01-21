import os
from pythonforandroid.toolchain import shprint, current_directory
from pythonforandroid.recipe import Recipe
from multiprocessing import cpu_count
import sh


class LibZBarRecipe(Recipe):

    version = '0.10'

    url = 'https://github.com/ZBar/ZBar/archive/{version}.zip'

    depends = ['libiconv']

    patches = ["werror.patch"]

    def should_build(self, arch):
        return not os.path.exists(
            os.path.join(self.ctx.get_libs_dir(arch.arch), 'libzbar.so'))

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super(LibZBarRecipe, self).get_recipe_env(arch, with_flags_in_cc)
        libiconv = self.get_recipe('libiconv', self.ctx)
        libiconv_dir = libiconv.get_build_dir(arch.arch)
        env['CFLAGS'] += ' -I' + os.path.join(libiconv_dir, 'include')
        env['LIBS'] = env.get('LIBS', '') + ' -landroid -liconv'
        return env

    def build_arch(self, arch):
        super(LibZBarRecipe, self).build_arch(arch)
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.Command('autoreconf'), '-vif', _env=env)
            shprint(
                sh.Command('./configure'),
                '--host=' + arch.toolchain_prefix,
                '--target=' + arch.toolchain_prefix,
                '--prefix=' + self.ctx.get_python_install_dir(),
                # Python bindings are compiled in a separated recipe
                '--with-python=no',
                '--with-gtk=no',
                '--with-qt=no',
                '--with-x=no',
                '--with-jpeg=no',
                '--with-imagemagick=no',
                '--enable-pthread=no',
                '--enable-video=no',
                '--enable-shared=yes',
                '--enable-static=no',
                _env=env)
            shprint(sh.make, '-j' + str(cpu_count()), _env=env)
            libs = ['zbar/.libs/libzbar.so']
            self.install_libs(arch, *libs)


recipe = LibZBarRecipe()
