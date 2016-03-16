
from pythonforandroid.toolchain import PythonRecipe, shprint, current_directory
from os.path import join
import sh


class ZopeInterfaceRecipe(PythonRecipe):
    name = 'zope_interface'
    version = '4.1.2'
    url = 'https://pypi.python.org/packages/source/z/zope.interface/zope.interface-{version}.tar.gz'
    site_packages_name = 'zope.interface'

    depends = ['python2']

    def build_arch(self, arch):
        super(ZopeInterfaceRecipe, self).build_arch(arch)
        print('Should remove zope tests etc. here, but skipping for now')

recipe = ZopeInterfaceRecipe()
