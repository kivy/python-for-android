from pythonforandroid.recipe import PythonRecipe


class IdnaRecipe(PythonRecipe):
	name = 'idna'
	version = '2.6'
	url = 'https://pypi.python.org/packages/f4/bd/0467d62790828c23c47fc1dfa1b1f052b24efdf5290f071c7a91d0d82fd3/idna-2.6.tar.gz#md5=c706e2790b016bd0ed4edd2d4ba4d147'

	depends = [('python2', 'python3crystax'), 'setuptools']

	call_hostpython_via_targetpython = False


recipe = IdnaRecipe()
