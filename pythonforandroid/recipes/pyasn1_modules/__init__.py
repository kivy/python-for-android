from pythonforandroid.recipe import PythonRecipe


class PyASN1ModulesRecipe(PythonRecipe):
    version = '0.2.2'
    url = 'https://pypi.python.org/packages/source/p/pyasn1-modules/pyasn1-modules-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools']
    site_packages_name = 'pyasn1_modules'


recipe = PyASN1ModulesRecipe()
