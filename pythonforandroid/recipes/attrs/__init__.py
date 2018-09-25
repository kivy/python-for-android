from pythonforandroid.recipe import PythonRecipe


class AttrsRecipe(PythonRecipe):
    version = '18.2.0'
    url = 'https://pypi.python.org/packages/source/a/attrs/attrs-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools']
    call_hostpython_via_targetpython = False


recipe = AttrsRecipe()
