
from pythonforandroid.toolchain import CythonRecipe, shprint, current_directory, ArchARM
from os.path import exists, join
import sh
import glob


class KivyRecipe(CythonRecipe):
    # version = 'stable'
    version = 'master'
    url = 'https://github.com/kivy/kivy/archive/{version}.zip'
    name = 'kivy'

    depends = [('sdl2', 'pygame'), 'pyjnius']

    # patches = ['setargv.patch']

    def get_recipe_env(self, arch):
        env = super(KivyRecipe, self).get_recipe_env(arch)
        if 'sdl2' in self.ctx.recipe_build_order:
            env['USE_SDL2'] = '1'
            env['KIVY_SDL2_PATH'] = ':'.join([
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include'),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_image'),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_mixer'),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
                ])
        return env

recipe = KivyRecipe()
