
from pythonforandroid.toolchain import PythonRecipe


class PyASN1Recipe(PythonRecipe):
    version = '0.1.8'
    url = 'https://pypi.python.org/packages/source/p/pyasn1/pyasn1-{version}.tar.gz'
    depends = ['python2']

recipe = PyASN1Recipe()
