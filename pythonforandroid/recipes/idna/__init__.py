from pythonforandroid.recipe import PythonRecipe


class IdnaRecipe(PythonRecipe):
	name = 'idna'
	version = '2.0'
	url = 'https://pypi.python.org/packages/source/i/idna/idna-{version}.tar.gz'

	depends = [('python2', 'python3'), 'setuptools']

	call_hostpython_via_targetpython = False


recipe = IdnaRecipe()
