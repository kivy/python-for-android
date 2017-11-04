from pythonforandroid.recipe import PythonRecipe


class IpaddressRecipe(PythonRecipe):
	name = 'ipaddress'
	version = '1.0.18'
        url = 'https://pypi.python.org/packages/4e/13/774faf38b445d0b3a844b65747175b2e0500164b7c28d78e34987a5bfe06/ipaddress-1.0.18.tar.gz#md5=310c2dfd64eb6f0df44aa8c59f2334a7'

	depends = ['python2']


recipe = IpaddressRecipe()
