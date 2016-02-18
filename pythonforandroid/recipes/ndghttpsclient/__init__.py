from pythonforandroid.toolchain import PythonRecipe

class NdgHttpsClientRecipe(PythonRecipe):
    version = '0.4.0'
    url = 'https://pypi.python.org/packages/source/n/ndg-httpsclient/ndg_httpsclient-{version}.tar.gz'
    depends = ['python2', 'pyopenssl', 'cryptography']
    call_hostpython_via_targetpython = False

recipe = NdgHttpsClientRecipe()
