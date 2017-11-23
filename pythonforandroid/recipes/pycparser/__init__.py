from pythonforandroid.recipe import PythonRecipe


class PycparserRecipe(PythonRecipe):
    name = 'pycparser'
    version = '2.18'
    url = 'https://pypi.python.org/packages/8c/2d/aad7f16146f4197a11f8e91fb81df177adcc2073d36a17b1491fd09df6ed/pycparser-2.18.tar.gz#md5=72370da54358202a60130e223d488136'

    depends = [('python2', 'python3crystax'), 'setuptools']

    call_hostpython_via_targetpython = False

    install_in_hostpython = True


recipe = PycparserRecipe()
