from pythonforandroid.recipe import NDKRecipe


class PngRecipe(NDKRecipe):
    name = 'png'
    version = '1.6.29'
    url = 'https://github.com/julienr/libpng-android/archive/master.zip'

    generated_libraries = ['libpng.a']


recipe = PngRecipe()
