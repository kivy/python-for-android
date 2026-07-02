from pythonforandroid.recipe import PyProjectRecipe


class SelectolaxRecipe(PyProjectRecipe):
    version = '0.4.10'
    url = 'https://pypi.python.org/packages/source/s/selectolax/selectolax-{version}.tar.gz'
    depends = ['setuptools']
    hostpython_prerequisites = ['cython==3.2.8']


recipe = SelectolaxRecipe()
