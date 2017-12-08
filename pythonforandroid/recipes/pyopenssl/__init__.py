from pythonforandroid.toolchain import PythonRecipe


class PyOpenSSLRecipe(PythonRecipe):
    version = 'master'
    url = 'git+file:///home/enoch/pyopenssl'
    depends = ['cryptography', 'six']
    site_packages_name = 'OpenSSL'

    call_hostpython_via_targetpython = False


recipe = PyOpenSSLRecipe()
