
from pythonforandroid.recipe import PythonRecipe


class PyOpenSSLRecipe(PythonRecipe):
    version = '24.1.0'
    url = 'https://pypi.python.org/packages/source/p/pyOpenSSL/pyOpenSSL-{version}.tar.gz'
    depends = ['cffi', 'openssl', 'setuptools']
    site_packages_name = 'OpenSSL'

    call_hostpython_via_targetpython = False


recipe = PyOpenSSLRecipe()
