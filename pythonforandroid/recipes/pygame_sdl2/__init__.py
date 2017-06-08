
from pythonforandroid.toolchain import Recipe, shprint, current_directory, ArchAndroid
from os.path import exists, join
import sh
import glob


class PygameSDL2Recipe(Recipe):
    # version = 'stable'
    version = 'master'
    url = 'https://github.com/renpy/pygame_sdl2/archive/{version}.zip'
    name = 'pygame_sdl2'

    depends = ['sdl2', 'pygame_sdl2_bootstrap_components']
    conflicts = ['pygame']

    def get_recipe_env(self, arch):
        env = super(PygameSDL2Recipe, self).get_recipe_env(arch)
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch))
        env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')
        env['LIBLINK'] = 'NOTNONE'
        env['NDKPLATFORM'] = self.ctx.ndk_platform
        env['CFLAGS'] = (env['CFLAGS'] +
                         ' -I{}'.format(join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include')) +
                         ' -I{}'.format(join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_image')) +
                         ' -I{}'.format(join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_mixer')) +
                         ' -I{}'.format(join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf')) +
                         ' -I{}'.format(join(self.ctx.bootstrap.build_dir, 'jni', 'jpeg')) +
                         ' -I{}'.format(join(self.ctx.bootstrap.build_dir, 'jni', 'png')) +
                         ' -I{}'.format(join(self.ctx.bootstrap.build_dir, 'jni', 'freetype', 'include'))
        )
        env['CXXFLAGS'] = env['CFLAGS']
        env['PYGAME_SDL2_ANDROID'] = 'yes'
        env['PYGAME_SDL2_EXCLUDE'] = 'pygame_sdl2.mixer pygame_sdl2.mixer_music'
        env['PYGAME_SDL2_INSTALL_HEADERS'] = '1'
        return env

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            try:
                sh.rm('-R', 'build/lib.android', 'build/tmp.android')
            except:
                pass
            hostpython = sh.Command(self.ctx.hostpython)
            env = self.get_recipe_env(arch)
            shprint(hostpython, 'setup.py', 'build_ext', '-b', 'build/lib.android', '-t',
                    'bluid/tmp.android', 'install',
                    '--prefix', '"{}"'.format(self.ctx.get_python_install_dir()),
                    _env=env)
            filens = glob.glob('build/lib.android/*')
            info('pygame_sdl2 filens to copy are {}'.format(filens))
            for filen in filens:
                shprint(sh.cp, '-a', filen, self.ctx.get_site_packages_dir() + '/pygame_sdl2')

recipe = PygameSDL2Recipe()
