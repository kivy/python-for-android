from pythonforandroid.recipe import PythonRecipe

class FeedparserPyRecipe(PythonRecipe):
	site_packages_name = 'feedparser'
	version = '5.2.1'
	url = 'https://github.com/kurtmckee/feedparser/archive/{version}.tar.gz'
	depends = [('hostpython2', 'python3crystax'), 'setuptools']
	call_hostpython_via_targetpython = False

recipe = FeedparserPyRecipe()