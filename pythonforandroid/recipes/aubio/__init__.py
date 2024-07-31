from pythonforandroid.recipe import CythonRecipe
from os.path import join


class AubioRecipe(CythonRecipe):
    version = "0.4.7"
    url = "https://aubio.org/pub/aubio-{version}.tar.bz2"
    depends = ["numpy"]  # Make sure 'samplerate' is included as a dependency
    patches = [join("patches", "build_ext.patch")]


recipe = AubioRecipe()
