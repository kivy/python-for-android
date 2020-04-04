from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.toolchain import current_directory
from os.path import join
import sh


class ZopeInterfaceRecipe(PythonRecipe):
    call_hostpython_via_targetpython = False
    name = 'zope_interface'
    version = '4.1.3'
    url = 'https://pypi.python.org/packages/source/z/zope.interface/zope.interface-{version}.tar.gz'
    site_packages_name = 'zope.interface'
    depends = ['setuptools']
    patches = ['no_tests.patch']

    def build_arch(self, arch):
        super().build_arch(arch)
        # The zope.interface module lacks of the __init__.py file in one of his
        # folders (once is installed), that leads into an ImportError.
        # Here we intentionally apply a patch to solve that, so, in case that
        # this is solved in the future an error will be triggered
        zope_install = join(self.ctx.get_site_packages_dir(arch.arch), 'zope')
        self.apply_patch('fix-init.patch', arch.arch, build_dir=zope_install)

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            sh.rm(
                '-rf',
                'src/zope/interface/tests',
                'src/zope/interface/common/tests',
            )


recipe = ZopeInterfaceRecipe()
