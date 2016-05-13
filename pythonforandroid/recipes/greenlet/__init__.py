from pythonforandroid.toolchain import PythonRecipe


class GreenletRecipe(PythonRecipe):
    version = '0.4.9'
    url = 'https://pypi.python.org/packages/source/g/greenlet/greenlet-{version}.tar.gz'
    depends = [('python2', 'python3crystax')]

recipe = GreenletRecipe()
