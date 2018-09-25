from pythonforandroid.recipe import PythonRecipe


class IpaddressRecipe(PythonRecipe):
    name = 'ipaddress'
    version = '1.0.22'
    url = 'https://pypi.python.org/packages/source/i/ipaddress/ipaddress-{version}.tar.gz'

    depends = [('python2', 'python3crystax')]


recipe = IpaddressRecipe()
