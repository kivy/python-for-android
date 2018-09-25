from pythonforandroid.recipe import PythonRecipe


class Asn1CryptoRecipe(PythonRecipe):
    version = '0.22.0'
    url = 'https://pypi.python.org/packages/source/a/asn1crypto/asn1crypto-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools']
    call_hostpython_via_targetpython = False


recipe = Asn1CryptoRecipe()
