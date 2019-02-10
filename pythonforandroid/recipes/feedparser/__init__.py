from pythonforandroid.recipe import PythonRecipe


class FeedparserPyRecipe(PythonRecipe):
    version = '5.2.1'
    url = 'https://github.com/kurtmckee/feedparser/archive/{version}.tar.gz'
    depends = ['setuptools']
    site_packages_name = 'feedparser'
    call_hostpython_via_targetpython = False


recipe = FeedparserPyRecipe()
