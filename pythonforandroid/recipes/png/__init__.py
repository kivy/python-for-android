from pythonforandroid.recipe import NDKRecipe
from pythonforandroid.logger import shprint
from pythonforandroid.toolchain import current_directory
from os.path import join, exists
import sh


class PngRecipe(NDKRecipe):
    name = 'png'
    version = '1.6.15'
    url = 'https://github.com/julienr/libpng-android/archive/{version}.zip'

    generated_libraries = ['libpng.a']

    def should_build(self, arch):
        if 'pygame' in self.ctx.recipe_build_order:
            return False
        return super(PngRecipe, self).should_build(arch)


recipe = PngRecipe()

