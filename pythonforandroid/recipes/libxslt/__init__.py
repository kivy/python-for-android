from pythonforandroid.toolchain import (CythonRecipe, shprint,
                                        current_directory, info, Recipe)
from pythonforandroid.patching import will_build, check_any
import sh
from os.path import exists,join

class LibxsltRecipe(CythonRecipe):
    version = '1.1.29'
    url = 'ftp://xmlsoft.org/libxslt/libxslt-{version}.tar.gz'
    name = 'libxslt'
    depends = [('python2', 'python3crystax'), 'libxml2']
    patches = ['fix-dlopen.patch']

    def should_build(self, arch):
        return not exists(join(self.get_build_dir(arch.arch),".libs/libxslt.a"))


    def get_recipe_env(self, arch):
        env = super(LibxsltRecipe, self).get_recipe_env(arch)
        sh.make('-j', '5')


recipe = LibxsltRecipe()
