
from pythonforandroid.toolchain import CythonRecipe, shprint, current_directory, info
import sh
import glob
from os.path import join, exists


class AudiostreamRecipe(CythonRecipe):
    version  = 'master'
    url = 'https://github.com/kivy/audiostream/archive/{version}.zip'
    name = 'audiostream'
    depends = ['python2', ('sdl', 'sdl2'), 'pyjnius']

    def get_recipe_env(self, arch):
        env = super(AudiostreamRecipe, self).get_recipe_env(arch)
        if 'sdl' in self.ctx.recipe_build_order:
            sdl_include = 'sdl'
            sdl_mixer_include = 'sdl_mixer'
        elif 'sdl2' in self.ctx.recipe_build_order:
            sdl_include = 'SDL2'
            sdl_mixer_include = 'SDL2_mixer'
            env['USE_SDL2'] = 'True'
            env['SDL2_INCLUDE_DIR'] = '/home/kivy/.buildozer/android/platform/android-ndk-r9c/sources/android/support/include'

        env['CFLAGS'] += ' -I{jni_path}/{sdl_include}/include -I{jni_path}/{sdl_mixer_include}'.format(
                              jni_path = join(self.ctx.bootstrap.build_dir, 'jni'),
                              sdl_include = sdl_include,
                              sdl_mixer_include = sdl_mixer_include)
        return env
        


recipe = AudiostreamRecipe()
