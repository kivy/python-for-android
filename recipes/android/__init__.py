
from toolchain import PythonRecipe, shprint, ensure_dir
import sh


class AndroidRecipe(PythonRecipe):
    # name = 'android'
    version = None
    url = None
    depends = ['pygame']

    def prebuild_armeabi(self):
        shprint(sh.cp, '-a', self.get_recipe_dir() + '/src', self.get_build_dir('armeabi'))
        


recipe = AndroidRecipe()
