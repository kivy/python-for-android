from pythonforandroid.recipe import CythonRecipe


class SelectolaxRecipe(CythonRecipe):
    version = '0.4.10'
    url = 'https://pypi.python.org/packages/source/s/selectolax/selectolax-{version}.tar.gz'
    depends = ['setuptools']


recipe = SelectolaxRecipe()