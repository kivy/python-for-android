from pythonforandroid.recipe import PythonRecipe


class SimpleCryptRecipe(PythonRecipe):
    version = '4.1.7'
    url = 'https://pypi.python.org/packages/source/s/simple-crypt/simple-crypt-{version}.tar.gz'
    depends = ['pycrypto']
    site_packages_name = 'simplecrypt'


recipe = SimpleCryptRecipe()
