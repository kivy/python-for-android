
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
        if 'sdl' in self.ctx.recipe_build_order:
            sdl_include = 'sdl'
            sdl_mixer_include = 'sdl_mixer'
        elif 'sdl2' in self.ctx.recipe_build_order:
            sdl_include = 'SDL'
            sdl_mixer_include = 'SDL2_mixer'
            
            #note: audiostream library is not yet able to judge whether it is being used with sdl or with sdl2.
            #this causes linking to fail against SDL2 (compiling against SDL2 works)
            #need to find a way to fix this in audiostream's setup.py
            raise RuntimeError('Audiostream library is not yet able to configure itself to link against SDL2.  Patch on audiostream library needed - any help much appreciated!')

        env = super(AudiostreamRecipe, self).get_recipe_env(arch)
        env['CFLAGS'] += ' -I{jni_path}/{sdl_include}/include -I{jni_path}/{sdl_mixer_include}'.format(
                              jni_path = join(self.ctx.bootstrap.build_dir, 'jni'),
                              sdl_include = sdl_include,
                              sdl_mixer_include = sdl_mixer_include)
        return env
        


recipe = AudiostreamRecipe()
