from pythonforandroid.recipe import PythonRecipe


class ServiceIdentityRecipe(PythonRecipe):
    version = '17.0.0'
    url = 'https://pypi.python.org/packages/source/s/service_identity/service_identity-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'setuptools', 'attrs', 'pyasn1-modules', 'pyopenssl', 'idna']
    call_hostpython_via_targetpython = False


recipe = ServiceIdentityRecipe()
