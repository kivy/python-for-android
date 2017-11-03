from pythonforandroid.toolchain import NDKRecipe, shprint, current_directory
from os.path import isdir, join
import sh


class LibIconv(NDKRecipe):
    generated_libraries = ['libiconv.a']

    def prebuild_arch(self, arch):
        super(LibIconv, self).prebuild_arch(arch)

        recipe_dir = self.get_recipe(self.name, arch.arch).recipe_dir
        src_dir = join(recipe_dir, 'src')
        if not isdir(self.get_build_dir(arch.arch)):
            shprint(sh.mkdir, self.get_build_dir(arch.arch))
        if not isdir(self.get_jni_dir(arch)):
            shprint(sh.mkdir, self.get_jni_dir(arch))
        shprint(sh.cp, "-a", "{}/.".format(src_dir),
                "{}".format(self.get_jni_dir(arch)))

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        env['NDK_PROJECT_PATH'] = self.get_build_dir(arch.arch)

        with current_directory(self.get_jni_dir(arch)):
            shprint(sh.ndk_build, "V=1", "iconv", _env=env)
        shprint(sh.cp, '-L', join(
            self.get_lib_dir(arch),
            'libiconv.{}'.format('a')),
            self.ctx.libs_dir)

recipe = LibIconv()
