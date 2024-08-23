from pythonforandroid.recipe import PyProjectRecipe
#from os.path import join


class AubioRecipe(PyProjectRecipe):
    version = "0.4.9"
    url = "https://aubio.org/pub/aubio-{version}.tar.bz2"
    depends = ["numpy", "setuptools"]  # Make sure 'samplerate' is included as a dependency
    #patches = [join("patches", "build_ext.patch")]


recipe = AubioRecipe()
