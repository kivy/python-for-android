
from pythonforandroid.recipe import PythonRecipe


class PyOpenSSLRecipe(PythonRecipe):
    version = '0.14'
    url = 'https://pypi.python.org/packages/source/p/pyOpenSSL/pyOpenSSL-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'openssl', 'setuptools']
    site_packages_name = 'OpenSSL'

    call_hostpython_via_targetpython = False


recipe = PyOpenSSLRecipe()
