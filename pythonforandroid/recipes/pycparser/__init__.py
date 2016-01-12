from pythonforandroid.recipe import PythonRecipe


class PycparserRecipe(PythonRecipe):
	name = 'pycparser'
	version = '2.14'
	url = 'https://pypi.python.org/packages/source/p/pycparser/pycparser-{version}.tar.gz'

	depends = [('python2', 'python3crystax'), 'setuptools']

	call_hostpython_via_targetpython = False

	install_in_hostpython = True


recipe = PycparserRecipe()
