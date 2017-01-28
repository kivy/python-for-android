

from pythonforandroid.toolchain import (CythonRecipe, shprint,
                                        current_directory, info, Recipe)
from pythonforandroid.patching import will_build, check_any
import sh
from os.path import join


class LxmlRecipe(CythonRecipe):
    version = '3.7.2'
    url = 'https://github.com/lxml/lxml/archive/lxml-{version}.tar.gz'
    name = 'lxml'
    depends = [('python2', 'python3crystax'), 'libxslt']

    def get_recipe_env(self, arch):
        env = super(LxmlRecipe, self).get_recipe_env(arch)

        libxslt_recipe = Recipe.get_recipe('libxslt', self.ctx)
        libxml2_recipe = Recipe.get_recipe('libxml2', self.ctx)

        env['CC'] = env['CC'] + ' -I{libxslt_dir}/include -I{libxslt_dir}'.format(
            librslt_dir=libxslt_recipe.get_build_dir(arch))

        env['LDFLAGS'] = ('-Llibxslt_dir/libxslt/.libs -Llibxslt_dir/libexslt/.libs '
                          '-Llibxml2_dir/.libs -Llibxslt_dir/libxslt -Llibxslt_dir/libexslt '
                          '-Llibxml2_dir/ ').format(libxslt_dir=libxslt_recipe.get_build_dir(arch),
                                                    libxml2_dir=libxml2_recipe.get_build_dir(arch))

        # env['LDSHARED'] = env['LIBLINK']  # not sure this is necessary in new toolchain

recipe = LxmlRecipe()
