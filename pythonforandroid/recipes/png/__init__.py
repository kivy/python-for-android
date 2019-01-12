from pythonforandroid.recipe import NDKRecipe


class PngRecipe(NDKRecipe):
    name = 'png'
    # This version is the last `sha commit` published in the repo (it's more
    # than one year old...) and it's for libpng version `1.6.29`. We set a
    # commit for a version because the author of the github's repo never
    # released/tagged it, despite He performed the necessary changes in
    # master branch.
    version = 'b43b4c6'

    # TODO: Try to move the repo to mainline
    url = 'https://github.com/julienr/libpng-android/archive/{version}.zip'

    generated_libraries = ['libpng.a']


recipe = PngRecipe()
