
from toolchain import PythonRecipe, shprint, ensure_dir, current_directory, ArchAndroid
import sh
from os.path import exists, join


class AndroidRecipe(PythonRecipe):
    # name = 'android'
    version = None
    url = None
    depends = ['pygame']

    def get_build_dir(self, arch):
        return join(self.get_build_container_dir('armeabi'), 'src')

    def prebuild_armeabi(self):
        shprint(sh.cp, '-a', self.get_recipe_dir() + '/src', self.get_build_dir('armeabi'))
        
    def build_armeabi(self):

        with current_directory(self.get_build_dir('armeabi')):
            if exists('.done'):
                print('android module already compiled, exiting')
                return

            env = ArchAndroid(self.ctx).get_env()

            env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(self.ctx.libs_dir)
            env['LDSHARED'] = env['LIBLINK']

            shprint(sh.find, '.', '-iname', '*.pyx', '-exec', self.ctx.cython, '{}', ';')

            hostpython = sh.Command(self.ctx.hostpython)
            shprint(hostpython, 'setup.py', 'build_ext', '-v', _env=env)
            shprint(hostpython, 'setup.py', 'install', '-O2', _env=env)

            shprint(sh.touch, '.done')
            


recipe = AndroidRecipe()
