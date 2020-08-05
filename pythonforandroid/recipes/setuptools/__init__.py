from pythonforandroid.recipe import PythonRecipe


class SetuptoolsRecipe(PythonRecipe):
    version = '49.2.1'
    url = 'https://pypi.python.org/packages/source/s/setuptools/setuptools-{version}.zip'
    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = SetuptoolsRecipe()
