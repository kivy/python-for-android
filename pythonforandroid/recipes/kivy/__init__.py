from pythonforandroid.toolchain import CythonRecipe
from os.path import join

class KivyRecipe(CythonRecipe):
    # version = 'stable'
    version = 'master'
    url = 'https://github.com/kivy/kivy/archive/{version}.zip'
    name = 'kivy'
    depends = [('sdl2', 'pygame'), 'pyjnius']
    call_hostpython_via_targetpython = False

    # patches = ['setargv.patch']

    def get_recipe_env(self, arch):
        env = super(KivyRecipe, self).get_recipe_env(arch)
        env['PYTHON_ROOT'] = self.ctx.get_python_install_dir()
        env['CFLAGS'] += ' -I' + env['PYTHON_ROOT'] + '/include/python2.7'
        env['LDFLAGS'] += ' -L' + env['PYTHON_ROOT'] + '/lib' + \
                          ' -lpython2.7'
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
