
from pythonforandroid.recipe import CythonRecipe
from os.path import join


class AudiostreamRecipe(CythonRecipe):
    version = 'master'
    url = 'https://github.com/kivy/audiostream/archive/{version}.zip'
    name = 'audiostream'
    depends = [('python2', 'python3'), ('sdl', 'sdl2'), 'pyjnius']

    def get_recipe_env(self, arch):
        env = super(AudiostreamRecipe, self).get_recipe_env(arch)
        if 'sdl' in self.ctx.recipe_build_order:
            sdl_include = 'sdl'
            sdl_mixer_include = 'sdl_mixer'
        elif 'sdl2' in self.ctx.recipe_build_order:
            sdl_include = 'SDL2'
            sdl_mixer_include = 'SDL2_mixer'
            env['USE_SDL2'] = 'True'
            env['SDL2_INCLUDE_DIR'] = join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include')

        env['CFLAGS'] += ' -I{jni_path}/{sdl_include}/include -I{jni_path}/{sdl_mixer_include}'.format(
                              jni_path=join(self.ctx.bootstrap.build_dir, 'jni'),
                              sdl_include=sdl_include,
                              sdl_mixer_include=sdl_mixer_include)
        env['NDKPLATFORM'] = self.ctx.ndk_platform
        env['LIBLINK'] = 'NOTNONE'  # Hacky fix. Needed by audiostream setup.py
        return env


recipe = AudiostreamRecipe()
