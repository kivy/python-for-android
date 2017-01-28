 
from pythonforandroid.toolchain import (PythonRecipe, shprint,
                                        current_directory, info, Recipe)
from pythonforandroid.patching import will_build, check_any
import sh
from os.path import join

class BSoup4Recipe(PythonRecipe):
    version = '4.1.0'
    url = 'https://www.crummy.com/software/BeautifulSoup/bs4/download/4.0/beautifulsoup4-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'lxml']
    site_packages_name = 'beautifulsoup4'
    call_hostpython_via_targetpython = True
    def get_recipe_env(self, arch):
        env = super(BSoup4Recipe, self).get_recipe_env(arch)

        
        lxml_recipe = Recipe.get_recipe('lxml', self.ctx)

        env['CC'] = env['CC'] + ' -I{lxml_dir}/include -I{lxml_dir}'.format(
            lxml_dir=lxml_recipe.get_build_dir(arch))

        env['LDFLAGS'] = ('-Llxml_dir/lxml/.libs -Llxml_dir/lxml/.libs ').format(lxml_dir=lxml_recipe.get_build_dir(arch))

recipe = BSoup4Recipe()