
from toolchain import PythonRecipe, shprint

class PygameRecipe(PythonRecipe):
    name = 'pygame'
    version = '1.9.1'
    url = 'http://pygame.org/ftp/pygame-{version}release.tar.gz'
    depends = ['python2', 'sdl']


recipe = PygameRecipe()
