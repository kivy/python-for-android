from pythonforandroid.recipe import PythonRecipe


class IpaddressRecipe(PythonRecipe):
    name = 'ipaddress'
    version = '1.0.22'
    url = 'https://github.com/phihag/ipaddress/archive/v{version}.tar.gz'

    depends = [('python2', 'python3', 'python3crystax')]


recipe = IpaddressRecipe()
