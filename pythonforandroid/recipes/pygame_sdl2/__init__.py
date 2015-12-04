
from pythonforandroid.toolchain import CythonRecipe, shprint, current_directory, ArchAndroid
from os.path import exists, join
import sh
import glob


class PygameSDL2Recipe(CythonRecipe):
    # version = 'stable'
    version = 'master'
    url = 'https://github.com/renpy/pygame_sdl2/archive/{version}.zip'
    name = 'pygame_sdl2'

    depends = ['sdl2']
    conflicts = ['pygame']

    def get_recipe_env(self, arch):
        env = super(PygameSDL2Recipe, self).get_recipe_env(arch)
        env['CFLAGS'] = (env['CFLAGS'] +
                         ' -I{}'.format(join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include')) +
                         ' -I{}'.format(join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_image')) +
                         ' -I{}'.format(join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_mixer')) +
                         ' -I{}'.format(join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf')) +
                         ' -LSDL2 -LSDL2_image -LSDL2_mixer -LSDL2_ttf')
        env['CXXFLAGS'] = env['CFLAGS']
        env['PYGAME_SDL2_ANDROID'] = 'yes'
        return env

recipe = PygameSDL2Recipe()
