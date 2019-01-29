from pythonforandroid.recipe import PythonRecipe


class BabelRecipe(PythonRecipe):
    name = 'babel'
    version = '2.2.0'
    url = 'https://pypi.python.org/packages/source/B/Babel/Babel-{version}.tar.gz'

    depends = ['setuptools', 'pytz']

    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = BabelRecipe()
