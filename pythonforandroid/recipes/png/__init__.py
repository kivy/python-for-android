from pythonforandroid.recipe import NDKRecipe


class PngRecipe(NDKRecipe):
    name = 'png'
    version = '1.6.15'
    url = 'https://github.com/julienr/libpng-android/archive/{version}.zip'

    generated_libraries = ['libpng.a']

    def should_build(self, arch):
        if 'pygame_bootstrap_components' in self.ctx.recipe_build_order:
            return False
        super(PngRecipe, self).should_build(arch)


recipe = PngRecipe()

