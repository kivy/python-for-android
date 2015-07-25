
from pythonforandroid.toolchain import CythonRecipe, shprint, current_directory, ArchAndroid
from os.path import exists, join
import sh
import glob


class KivyRecipe(CythonRecipe):
    # version = 'stable'
    version = 'master'
    url = 'https://github.com/kivy/kivy/archive/{version}.zip'
    name = 'kivy'

    depends = [('sdl2', 'pygame'), 'pyjnius']

    def prebuild_arch(self, arch):
        super(KivyRecipe, self).prebuild_arch(arch)
        if 'sdl2' in self.ctx.recipe_build_order:
            build_dir = self.get_build_dir(arch.arch)
            if exists(join(build_dir, '.patched')):
                print('kivysdl2 already patched, skipping')
                return
            self.apply_patch('android_sdl2_compat.patch')
            shprint(sh.touch, join(build_dir, '.patched'))

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
