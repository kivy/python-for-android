from pythonforandroid.recipe import PythonRecipe


class IpaddressRecipe(PythonRecipe):
	name = 'ipaddress'
	version = '1.0.16'
	url = 'https://pypi.python.org/packages/source/i/ipaddress/ipaddress-{version}.tar.gz'

	depends = ['python2']


recipe = IpaddressRecipe()
