from pythonforandroid.toolchain import NDKRecipe, shprint, shutil, current_directory
from os.path import join, exists
import sh


class Sqlite3Recipe(NDKRecipe):
    version = '3.11.0'
    # Don't forget to change the URL when changing the version
    url = 'http://www.sqlite.com/2016/sqlite-amalgamation-3110000.zip'
    generated_libraries = ['sqlite3']

    def should_build(self, arch):
        if 'pygame_bootstrap_components' in self.ctx.recipe_build_order:
            return False
        return not self.has_libs(arch, 'libsqlite3.so')

    def get_lib_dir(self, arch):
        return join(self.get_build_dir(arch.arch), 'libs', arch.arch)

    def prebuild_arch(self, arch):
        super(Sqlite3Recipe, self).prebuild_arch(arch)
        # Copy the Android make file
        sh.mkdir('-p', join(self.get_build_dir(arch.arch), 'jni'))
        shutil.copyfile(join(self.get_recipe_dir(), 'Android.mk'),
                        join(self.get_build_dir(arch.arch), 'jni/Android.mk'))

    def build_arch(self, arch, *extra_args):
        super(Sqlite3Recipe, self).build_arch(arch)
        # Copy the shared library
        self.install_libs(arch, join(self.get_lib_dir(arch), 'libsqlite3.so'))

    def get_recipe_env(self, arch):
        env = super(Sqlite3Recipe, self).get_recipe_env(arch)
        env['NDK_PROJECT_PATH'] = self.get_build_dir(arch.arch)
        return env

recipe = Sqlite3Recipe()
