from pythonforandroid.recipe import PythonRecipe


class Host_setuptools_recipe(PythonRecipe):
    name = 'setuptools'

    depends = ['host_pip']

    def unpack(self, arch):
        return

    def build_arch(self, arch):
        self.pip_install_hostpython_package(arch)


recipe = Host_setuptools_recipe()
