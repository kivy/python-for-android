
from pythonforandroid.recipe import PythonRecipe


class PyOpenSSLRecipe(PythonRecipe):
    version = '19.0.0'
    url = 'https://pypi.python.org/packages/source/p/pyOpenSSL/pyOpenSSL-{version}.tar.gz'
    depends = ['openssl', 'setuptools']
    site_packages_name = 'OpenSSL'

    call_hostpython_via_targetpython = False


recipe = PyOpenSSLRecipe()
