from pythonforandroid.recipe import PythonRecipe


class Enum34Recipe(PythonRecipe):
    version = '1.1.3'
    url = 'https://pypi.python.org/packages/source/e/enum34/enum34-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools']
    site_packages_name = 'enum'
    call_hostpython_via_targetpython = False


recipe = Enum34Recipe()
