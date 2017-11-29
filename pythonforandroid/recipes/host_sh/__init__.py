from pythonforandroid.recipe import PythonRecipe


class Host_sh_recipe(PythonRecipe):
    name = 'sh'

    depends = ['host_pip']

    def unpack(self, arch):
        return

    def build_arch(self, arch):
        self.pip_install_hostpython_package(arch)


recipe = Host_sh_recipe()
