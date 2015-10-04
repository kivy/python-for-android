
from pythonforandroid.toolchain import PythonRecipe, shprint, current_directory
from os.path import join
import sh


class ZopeRecipe(PythonRecipe):
    version = '4.1.2'
    url = 'https://pypi.python.org/packages/source/z/zope.interface/zope.interface-{version}.tar.gz'

    depends = ['python2']

    def build_arch(self, arch):
        super(ZopeRecipe, self).build_arch(arch)
        print('Should remove zope tests etc. here, but skipping for now')

recipe = ZopeRecipe()
