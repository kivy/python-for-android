from pythonforandroid.toolchain import BootstrapNDKRecipe, shprint, ArchARM, current_directory, info
from os.path import exists, join
import sh

class LibSDLRecipe(BootstrapNDKRecipe):
    version = "1.2.14"
    url = None  
    name = 'sdl'
    depends = ['python2', 'pygame_bootstrap_components']
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

    def get_recipe_env(self, arch=None):
        env = super(LibSDLRecipe, self).get_recipe_env(arch)
        py2 = self.get_recipe('python2', arch.ctx)
        env['PYTHON2_NAME'] = py2.get_dir_name()
        if 'python2' in self.ctx.recipe_build_order:
            env['EXTRA_LDLIBS'] = ' -lpython2.7'
        return env


recipe = LibSDLRecipe()
