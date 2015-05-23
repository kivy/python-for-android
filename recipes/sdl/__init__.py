from toolchain import NDKRecipe, shprint, ArchAndroid, current_directory
from os.path import exists, join
import sh

class LibSDLRecipe(NDKRecipe):
    version = "1.2.14"
    url = None  
    name = 'sdl'
    depends = ['python2']

    def prebuild_armeabi(self):
        print('Debug: sdl recipe dir is ' + self.get_build_container_dir('armeabi'))

    def build_armeabi(self):

        if exists(join(self.ctx.libs_dir, 'libsdl.so')):
            print('libsdl.so already exists, skipping sdl build.')
            return
        
        env = ArchAndroid(self.ctx).get_env()

        print('env is', env)

        with current_directory(self.get_jni_dir()):
            shprint(sh.ndk_build, 'V=1', _env=env)

        libs_dir = join(self.ctx.bootstrap.build_dir, 'libs', 'armeabi')
        import os
        print('libs dir is', libs_dir)
        contents = list(os.walk(libs_dir))[0][-1]
        print('contents are', contents)
        for content in contents:
            shprint(sh.cp, '-a', join(self.ctx.bootstrap.build_dir, 'libs', 'armeabi', content),
                    self.ctx.libs_dir)


recipe = LibSDLRecipe()

