from toolchain import NDKRecipe, shprint, ArchAndroid, current_directory, info
from os.path import exists, join
import sh

class LibSDLRecipe(NDKRecipe):
    version = "1.2.14"
    url = None  
    name = 'sdl'
    depends = ['python2']

    def build_armeabi(self):

        if exists(join(self.ctx.libs_dir, 'libsdl.so')):
            info('libsdl.so already exists, skipping sdl build.')
            return
        
        env = ArchAndroid(self.ctx).get_env()

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, 'V=1', _env=env)

        libs_dir = join(self.ctx.bootstrap.build_dir, 'libs', 'armeabi')
        import os
        contents = list(os.walk(libs_dir))[0][-1]
        for content in contents:
            shprint(sh.cp, '-a', join(self.ctx.bootstrap.build_dir, 'libs', 'armeabi', content),
                    self.ctx.libs_dir)


recipe = LibSDLRecipe()
