from pythonforandroid.recipe import PythonRecipe


class Asn1cryptoRecipe(PythonRecipe):
    name = 'asn1crypto'
    version = '0.23.0'
    url = 'https://pypi.python.org/packages/31/53/8bca924b30cb79d6d70dbab6a99e8731d1e4dd3b090b7f3d8412a8d8ffbc/asn1crypto-0.23.0.tar.gz#md5=97d54665c397b72b165768398dfdd876'
    depends = ['python2', 'setuptools']

    call_hostpython_via_targetpython = False


recipe = Asn1cryptoRecipe()
