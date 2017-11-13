from pythonforandroid.toolchain import PythonRecipe


class SimpleCryptRecipe(PythonRecipe):
    version = '4.1.7'
    url = 'https://pypi.python.org/packages/source/s/simple-crypt/simple-crypt-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'pycrypto']
    site_packages_name = 'simplecrypt'

recipe = SimpleCryptRecipe()
