
from pythonforandroid.recipe import PythonRecipe


class SixRecipe(PythonRecipe):
    version = '1.9.0'
    url = 'https://pypi.python.org/packages/source/s/six/six-{version}.tar.gz'


recipe = SixRecipe()
