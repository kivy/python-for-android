from pythonforandroid.recipe import CythonRecipe


class GroestlcoinHashRecipe(CythonRecipe):
    version = '1.0.1'
    url = 'https://github.com/Groestlcoin/groestlcoin-hash-python/archive/{version}.tar.gz'
    depends = []
    cythonize = False


recipe = GroestlcoinHashRecipe()
