from pythonforandroid.recipe import CythonRecipe


class GroestlcoinHashRecipe(CythonRecipe):
    version = '1.0.3'
    url = 'https://github.com/Groestlcoin/groestlcoin-hash-python/archive/{version}.tar.gz'
    depends = ['setuptools']
    cythonize = False


recipe = GroestlcoinHashRecipe()
