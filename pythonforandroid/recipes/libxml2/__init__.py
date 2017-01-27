from pythonforandroid.toolchain import (CythonRecipe, shprint,
                                        current_directory, info, Recipe)
from pythonforandroid.patching import will_build, check_any
import sh
from os.path import join


class Libxml2Recipe(CythonRecipe):
    version = '2.9.4'
    url = 'ftp://xmlsoft.org/libxml2/libxml2-{version}.tar.gz'
    name = 'libxml2'
    depends = [('python2', 'python3crystax')]

    def get_recipe_env(self, arch):
        env = super(Libxml2Recipe, self).get_recipe_env(arch)

        try:
            sh.sed('runtest\$(EXEEXT) \\/ \\/', 'Makefile')
        except:
            pass
        try:
            sh.sed('testrecurse\$(EXEEXT)$//', 'Makefile')
        except:
            pass
        try:
            sh.make('-j', '$MAKE_JOBS')
        except:
            pass
        

recipe = Libxml2Recipe()
