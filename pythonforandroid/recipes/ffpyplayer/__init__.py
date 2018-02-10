from pythonforandroid.toolchain import Recipe, CythonRecipe, shprint, current_directory, ArchARM
from os.path import exists, join, realpath
from platform import uname
import glob
try:
    import sh
except ImportError:
    # fallback: emulate the sh API with pbs
    import pbs
    class Sh(object):
        def __getattr__(self, attr):
            return pbs.Command(attr)
    sh = Sh()

import os


class FFPyPlayerRecipe(CythonRecipe):
    version = '6f7568b498715c2da88f061ebad082a042514923'
    url = 'https://github.com/matham/ffpyplayer/archive/{version}.zip'
    depends = [('python2', 'python3crystax'), 'sdl2', 'ffmpeg']
    opt_depends = ['openssl', 'ffpyplayer_codecs']

    def get_recipe_env(self, arch, with_flags_in_cc=True):
        env = super(FFPyPlayerRecipe, self).get_recipe_env(arch)

        build_dir = Recipe.get_recipe('ffmpeg', self.ctx).get_build_dir(arch.arch)
        env["FFMPEG_INCLUDE_DIR"] = join(build_dir, "include")
        env["FFMPEG_LIB_DIR"] = join(build_dir, "lib")

        env["SDL_INCLUDE_DIR"] = join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include')
        env["SDL_LIB_DIR"] = join(self.ctx.bootstrap.build_dir, 'libs', arch.arch)

        env["USE_SDL2_MIXER"] = '1'
        env["SDL2_MIXER_INCLUDE_DIR"] = join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_mixer')

        return env

recipe = FFPyPlayerRecipe()
