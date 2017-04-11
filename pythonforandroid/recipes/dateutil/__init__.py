from pythonforandroid.recipe import PythonRecipe


class DateutilRecipe(PythonRecipe):
	name = 'dateutil'
	version = '2.6.0'
	url = 'https://pypi.python.org/packages/3e/f5/aad82824b369332a676a90a8c0d1e608b17e740bbb6aeeebca726f17b902/python-dateutil-{version}.tar.gz'

	depends = ['python2', "setuptools"]
	call_hostpython_via_targetpython = False
	install_in_hostpython = True


recipe = DateutilRecipe()
