from pythonforandroid.toolchain import NDKRecipe, shutil
from pythonforandroid.logger import shprint
from pythonforandroid.util import ensure_dir
from os.path import join
import sh

class Sqlite3Recipe(NDKRecipe):
    version = '3.11.0'
    # Don't forget to change the URL when changing the version
    url = 'http://www.sqlite.com/2016/sqlite-amalgamation-3110000.zip'
    generated_libraries = ['sqlite3']

    def should_build(self, arch):
        return not self.has_libs(arch, 'libsqlite3.so')

    def get_jni_dir(self, arch):
        if 'pygame' in self.ctx.recipe_build_order:
            return join(self.ctx.bootstrap.build_dir, 'jni')
        return join(self.get_build_dir(arch.arch), 'jni')

    def get_lib_dir(self, arch):
        if 'pygame' in self.ctx.recipe_build_order:
            return join(self.get_jni_dir(arch), 'sqlite3')
        return join(self.get_build_dir(arch.arch), 'libs', arch.arch)

    def prebuild_arch(self, arch):
        super(Sqlite3Recipe, self).prebuild_arch(arch)
        # Copy the Android make file
        sh.mkdir('-p', join(self.get_build_dir(arch.arch), 'jni'))
        shutil.copyfile(join(self.get_recipe_dir(), 'Android.mk'),
                        join(self.get_build_dir(arch.arch), 'jni/Android.mk'))

    def build_arch(self, arch, *extra_args):
        super(Sqlite3Recipe, self).build_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        self.install_libs(arch, join(build_dir, 'libs', arch.arch, 'libsqlite3.so'))

        # If building with the pygame bootstrap, we must integrate libsqlite3 and
        # all the include files into the bootstrap directory, because depends on it...
        if 'pygame' in self.ctx.recipe_build_order:
            lib_dir = join(self.get_jni_dir(arch), 'sqlite3')
            ensure_dir(lib_dir)
            shprint(sh.cp, join(self.get_recipe_dir(), 'Android_prebuilt.mk'),
                    join(lib_dir, 'Android.mk'))
            shprint(sh.cp, join(build_dir, 'libs', arch.arch, 'libsqlite3.so'),
                    join(lib_dir, 'libsqlite3.so'))
            shprint(sh.cp, join(build_dir, 'sqlite3.h'),
                    join(lib_dir, 'sqlite3.h'))
            shprint(sh.cp, join(build_dir, 'sqlite3ext.h'),
                    join(lib_dir, 'sqlite3ext.h'))

    def get_recipe_env(self, arch):
        env = super(Sqlite3Recipe, self).get_recipe_env(arch)
        env['NDK_PROJECT_PATH'] = self.get_build_dir(arch.arch)
        return env

recipe = Sqlite3Recipe()
