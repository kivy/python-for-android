from pythonforandroid.recipe import PythonRecipe


class Host_cffi_recipe(PythonRecipe):
    name = 'cffi'
    version = '1.11.2'

    depends = ['host_pip']

    def unpack(self, arch):
        return

    def build_arch(self, arch):
        self.pip_install_hostpython_package(arch)


recipe = Host_cffi_recipe()
