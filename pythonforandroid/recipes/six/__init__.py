
from pythonforandroid.recipe import PythonRecipe


class SixRecipe(PythonRecipe):
    version = '1.9.0'
    url = 'https://pypi.python.org/packages/source/s/six/six-{version}.tar.gz'
    depends = [('python2', 'python2legacy', 'python3', 'python3crystax')]
    # this recipe seems to control the dependency graph in some way, because
    # if removed the python2legacy recipe fails to solve the dependency order
    # when using the pygame bootstrap...so be careful removing this line!!!


recipe = SixRecipe()
