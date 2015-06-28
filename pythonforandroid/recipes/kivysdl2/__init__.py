
from pythonforandroid.toolchain import CythonRecipe, shprint, current_directory, ArchAndroid
from os.path import exists, join
import sh
import glob


class KivySDL2Recipe(CythonRecipe):
    # version = 'stable'
    version = 'master'
    url = 'https://github.com/kivy/kivy/archive/{version}.zip'
    site_packages_name = 'kivy'

    depends = ['sdl2', 'python2', 'pyjniussdl2']

    def prebuild_arch(self, arch):
        super(KivySDL2Recipe, self).prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        if exists(join(build_dir, '.patched')):
            print('kivysdl2 already patched, skipping')
            return
        self.apply_patch('android_sdl2_compat.patch')
        shprint(sh.touch, join(build_dir, '.patched'))

    def get_recipe_env(self, arch):
        env = super(KivySDL2Recipe, self).get_recipe_env(arch)
        env['USE_SDL2'] = '1'

        env['KIVY_SDL2_PATH'] = ':'.join([
            join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include'),
            join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_image'),
            join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_mixer'),
            join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
            ])
        return env
        
    # def build_armeabi(self):
    #     env = ArchAndroid(self.ctx).get_env()

    #     env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(self.ctx.libs_dir)
    #     env['LDSHARED'] = env['LIBLINK']

    #     # AND: Hack to make pyjnius setup.py detect android build
    #     env['NDKPLATFORM'] = 'NOTNONE'

    #     with current_directory(self.get_build_dir('armeabi')):
    #         if exists('.done'):
    #             print('android module already compiled, exiting')
    #             return

    #         hostpython = sh.Command(self.ctx.hostpython)
            
    #         print('First build attempt will fail as hostpython doesn\'t have cython available:')
    #         try:
    #             shprint(hostpython, 'setup.py', 'build_ext', _env=env)
    #         except sh.ErrorReturnCode_1:
    #             print('failed (as expected)')
    #         print('Running cython where appropriate')
    #         shprint(sh.find, self.get_build_dir('armeabi'), '-iname', '*.pyx', '-exec',
    #                 self.ctx.cython, '{}', ';', _env=env)
    #         print('ran cython')

    #         shprint(hostpython, 'setup.py', 'build_ext', '-v', _env=env)

    #         build_lib = glob.glob('./build/lib*')
    #         shprint(sh.find, build_lib[0], '-name', '*.o', '-exec',
    #                 env['STRIP'], '{}', ';', _env=env)

    #         shprint(hostpython, 'setup.py', 'install', '-O2', _env=env)

    #         # AND: Should check in site-packages instead!
    #         sh.touch('.done')

recipe = KivySDL2Recipe()
