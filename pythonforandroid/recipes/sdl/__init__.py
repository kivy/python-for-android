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
        
        env = arch.get_env()

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, 'V=1', _env=env, _tail=20, _critical=True)

        libs_dir = join(self.ctx.bootstrap.build_dir, 'libs', arch.arch)
        import os
        contents = list(os.walk(libs_dir))[0][-1]
        for content in contents:
            shprint(sh.cp, '-a', join(self.ctx.bootstrap.build_dir, 'libs', arch.arch, content),
                    self.ctx.libs_dir)


recipe = LibSDLRecipe()
