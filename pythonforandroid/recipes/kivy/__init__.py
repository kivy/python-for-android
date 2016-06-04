
from pythonforandroid.toolchain import CythonRecipe
from os.path import join


class KivyRecipe(CythonRecipe):
    version = 'master'
    url = 'https://github.com/kivy/kivy/archive/{version}.zip'
    name = 'kivy'

    depends = [('sdl2', 'pygame'), 'pyjnius', 'setuptools', 'wheel']

    call_hostpython_via_targetpython = False

    use_pip = True
    wheel_name = 'Kivy'

    def get_recipe_env(self, arch):
        env = super(KivyRecipe, self).get_recipe_env(arch)
        env['KIVY_USE_SETUPTOOLS'] = '1'
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
