
from pythonforandroid.toolchain import PythonRecipe


class PyOpenSSLRecipe(PythonRecipe):
    version = '17.4.0'
    url = 'https://pypi.python.org/packages/41/63/8759b18f0a240e91a24029e7da7c4a95ab75bca9028b02635ae0a9723c23/pyOpenSSL-17.4.0.tar.gz#md5=3abf7e09c38cb6d1019ef62ce7d1b1b2'
    depends = ['cryptography', 'six']
    site_packages_name = 'OpenSSL'

    call_hostpython_via_targetpython = False


recipe = PyOpenSSLRecipe()
