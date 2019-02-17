
from pythonforandroid.recipe import PythonRecipe


class PyASN1Recipe(PythonRecipe):
    version = '0.4.5'
    url = 'https://pypi.python.org/packages/source/p/pyasn1/pyasn1-{version}.tar.gz'
    depends = []


recipe = PyASN1Recipe()
