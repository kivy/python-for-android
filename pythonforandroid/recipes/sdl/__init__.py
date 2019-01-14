from pythonforandroid.recipe import BootstrapNDKRecipe
from pythonforandroid.toolchain import current_directory, info, shprint
from os.path import exists, join
import sh


class LibSDLRecipe(BootstrapNDKRecipe):
    version = "1.2.14"
    url = None
    name = 'sdl'
    depends = ['python2legacy', 'pygame_bootstrap_components']
    conflicts = ['sdl2']

    def build_arch(self, arch):

        if exists(join(self.ctx.libs_dir, 'libsdl.so')):
            info('libsdl.so already exists, skipping sdl build.')
            return

        env = self.get_recipe_env(arch)

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, 'V=1', _env=env, _tail=20, _critical=True)

        libs_dir = join(self.ctx.bootstrap.build_dir, 'libs', arch.arch)
        import os
        contents = list(os.walk(libs_dir))[0][-1]
        for content in contents:
            shprint(sh.cp, '-a', join(self.ctx.bootstrap.build_dir, 'libs', arch.arch, content),
                    self.ctx.libs_dir)

    def get_recipe_env(self, arch=None, with_flags_in_cc=True, with_python=True):
        env = super(LibSDLRecipe, self).get_recipe_env(
            arch=arch, with_flags_in_cc=with_flags_in_cc, with_python=with_python)
        return env


recipe = LibSDLRecipe()
