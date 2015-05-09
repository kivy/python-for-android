
from toolchain import PythonRecipe, shprint
from os.path import exists, join
import sh

class PygameRecipe(PythonRecipe):
    name = 'pygame'
    version = '1.9.1'
    url = 'http://pygame.org/ftp/pygame-{version}release.tar.gz'
    depends = ['python2', 'sdl']

    def prebuild_armeabi(self):
        if exists(join(self.get_build_dir('armeabi'), '.patched')):
            print('Pygame already patched, skipping.')
            return
        self.apply_patch(join('patches', 'fix-surface-access.patch'))
        self.apply_patch(join('patches', 'fix-array-surface.patch'))
        shprint(sh.touch, join(self.get_build_dir('armeabi'), '.patched'))
        


recipe = PygameRecipe()
