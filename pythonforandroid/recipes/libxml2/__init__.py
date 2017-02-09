from pythonforandroid.toolchain import (CythonRecipe, shprint,
                                        current_directory, info, Recipe)
from pythonforandroid.patching import will_build, check_any
import sh
from os.path import join


class Libxml2Recipe(Recipe):
    version = '2.9.3'
    url = 'ftp://xmlsoft.org/libxml2/libxml2-{version}.tar.gz'
    name = 'libxml2'
    depends = [('python2', 'python3crystax')]

    def get_recipe_env(self, arch):
        env = super(Libxml2Recipe, self).get_recipe_env(arch)
        return env

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            sh.sed('runtest$(EXEEXT)', 'Makefile')
            sh.sed('testrecurse$(EXEEXT)', 'Makefile')
            sh.make('-j', '5')
        

recipe = Libxml2Recipe()
