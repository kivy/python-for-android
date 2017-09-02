
from pythonforandroid.toolchain import PythonRecipe, shprint, current_directory
from os.path import exists, join
import sh
import glob

class ZopeRecipe(PythonRecipe):
    name = 'zope'
    version = '4.1.3'
    url = 'http://pypi.python.org/packages/source/z/zope.interface/zope.interface-{version}.tar.gz'

    depends = ['python2']
    
    def get_recipe_env(self, arch):
        env = super(ZopeRecipe, self).get_recipe_env(arch)

        # These are in the old zope recipe but seem like they shouldn't actually be necessary
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{}'.format(
            self.ctx.get_libs_dir(arch.arch))
        env['LDSHARED'] = join(self.ctx.root_dir, 'tools', 'liblink')

    def postbuild_arch(self, arch):
        super(ZopeRecipe, self).postbuild_arch(arch)

        # Should do some deleting here

recipe = ZopeRecipe()
