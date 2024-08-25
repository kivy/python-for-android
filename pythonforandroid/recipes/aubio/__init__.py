"""
Aubio recipe.
Note that this hasn't been ported to cross compile from macOS yet,
the error on 0.4.9 was: src/aubio_priv.h:95:10:
fatal error: 'Accelerate/Accelerate.h' file not found
#include <Accelerate/Accelerate.h>
"""

from pythonforandroid.recipe import PyProjectRecipe


class AubioRecipe(PyProjectRecipe):
    version = "0.4.9"
    url = "https://aubio.org/pub/aubio-{version}.tar.bz2"
    depends = ["numpy", "setuptools"]


recipe = AubioRecipe()
