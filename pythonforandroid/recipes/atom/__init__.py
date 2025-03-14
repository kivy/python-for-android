from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class AtomRecipe(CppCompiledComponentsPythonRecipe):
    site_packages_name = 'atom'
    version = '0.11.0'
    url = 'https://github.com/nucleic/atom/archive/refs/tags/{version}.zip'
    hostpython_prerequisites = ['cppy']
    depends = ['setuptools']

    def build_arch(self, arch):
        if arch.arch in ["armeabi-v7a", "x86"]:
            warning("*******************************************")
            warning("******** atom recipe was not built ********")
            warning("* atom does not support 32 bit platforms **")
            warning("*** Expect the following run time error ***")
            warning("ModuleNotFoundError: No module named 'atom'")
            warning("*******************************************")
        else:
            super().build_arch(arch)


recipe = AtomRecipe()
