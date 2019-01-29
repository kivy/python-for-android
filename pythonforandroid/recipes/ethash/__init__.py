from pythonforandroid.recipe import PythonRecipe


class EthashRecipe(PythonRecipe):

    url = 'https://github.com/ethereum/ethash/archive/master.zip'

    depends = ['setuptools']


recipe = EthashRecipe()
