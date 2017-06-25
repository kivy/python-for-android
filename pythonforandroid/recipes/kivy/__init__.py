
from pythonforandroid.toolchain import CythonRecipe, shprint, current_directory, ArchARM
from os.path import exists, join
import pythonforandroid.sh as sh
import glob


class KivyRecipe(CythonRecipe):
    version = '1.10.0'
    url = 'https://github.com/kivy/kivy/archive/{version}.zip'
    name = 'kivy'

    depends = [('sdl2', 'pygame'), 'pyjnius']

    # patches = ['setargv.patch']

    def cythonize_build(self, env, build_dir='.'):
        super(KivyRecipe, self).cythonize_build(env, build_dir=build_dir)

        if not exists(join(build_dir, 'kivy', 'include')):
            return

        # If kivy is new enough to use the include dir, copy it
        # manually to the right location as we bypass this stage of
        # the build
        with current_directory(build_dir):
            build_libs_dirs = glob.glob(join('build', 'lib.*'))

            for dirn in build_libs_dirs:
                shprint(sh.cp, '-r', join('kivy', 'include'),
                        join(dirn, 'kivy'))

    def get_recipe_env(self, arch):
        env = super(KivyRecipe, self).get_recipe_env(arch)
        if 'KIVY_USE_SETUPTOOLS' in env:
            del env['KIVY_USE_SETUPTOOLS']
        if 'USE_GSTREAMER' in env:
            del env['USE_GSTREAMER']
        if 'sdl2' in self.ctx.recipe_build_order:
            env['USE_SDL2'] = '1'
            env['KIVY_SPLIT_EXAMPLES'] = '1'
            env['KIVY_SDL2_PATH'] = ':'.join([
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include'),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_image'),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_mixer'),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
                ])

        return env

recipe = KivyRecipe()
