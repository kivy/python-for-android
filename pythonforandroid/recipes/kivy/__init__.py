
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
        if 'sdl2' in self.ctx.recipe_build_order:
            env['CUR_ARCH'] = arch.arch
            env['USE_SDL2'] = '1'
            env['KIVY_SDL2_PATH'] = ':'.join([
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include'),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_image'),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_mixer'),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
                ])

        # Set include dir for pxi files - Kivy normally handles this
        # in the setup.py invocation, but we skip this
        build_dir = self.get_build_dir(arch.arch)
        self.cython_args = ['-I{}'.format(join(build_dir, 'kivy', 'include'))]

        env['CFLAGS'] += ' -I{}'.format(join(build_dir, 'kivy', 'include'))

        return env

recipe = KivyRecipe()
