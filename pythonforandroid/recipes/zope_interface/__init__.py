from pythonforandroid.toolchain import PythonRecipe

class ZopeInterfaceRecipe(PythonRecipe):
    name = 'zope_interface'
    version = '4.1.2'
    url = 'https://pypi.python.org/packages/source/z/zope.interface/zope.interface-{version}.tar.gz'
    depends = ['python2']
    call_hostpython_via_targetpython = False
    site_packages_name = 'zope.interface'

    def build_arch(self, arch):
        super(ZopeInterfaceRecipe, self).build_arch(arch)
        print('Should remove zope tests etc. here, but skipping for now')

recipe = ZopeInterfaceRecipe()
