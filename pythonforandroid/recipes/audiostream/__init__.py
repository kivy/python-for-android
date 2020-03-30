
from pythonforandroid.recipe import CythonRecipe
from os.path import join


class AudiostreamRecipe(CythonRecipe):
    version = 'master'
    url = 'https://github.com/kivy/audiostream/archive/{version}.zip'
    name = 'audiostream'
    depends = ['python3', 'sdl2', 'pyjnius']

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
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
