from pythonforandroid.recipe import PythonRecipe


class SetuptoolsRecipe(PythonRecipe):
    version = '40.0.0'
    url = 'https://pypi.python.org/packages/source/s/setuptools/setuptools-{version}.zip'

    depends = [('python2', 'python3crystax')]

    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = SetuptoolsRecipe()
