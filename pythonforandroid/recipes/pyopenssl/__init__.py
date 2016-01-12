
from pythonforandroid.toolchain import PythonRecipe


class PyOpenSSLRecipe(PythonRecipe):
    version = '0.14'
    url = 'https://pypi.python.org/packages/source/p/pyOpenSSL/pyOpenSSL-{version}.tar.gz'
    depends = ['openssl', 'python2', 'setuptools']
    site_packages_name = 'OpenSSL'

    call_hostpython_via_targetpython = False


recipe = PyOpenSSLRecipe()
