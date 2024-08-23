from pythonforandroid.recipe import PyProjectRecipe


class AubioRecipe(PyProjectRecipe):
    version = "0.4.9"
    url = "https://aubio.org/pub/aubio-{version}.tar.bz2"
    depends = ["numpy", "setuptools"]


recipe = AubioRecipe()
