from pythonforandroid.recipe import PythonRecipe


class SetuptoolsRecipe(PythonRecipe):
    version = '69.0.3'
    url = 'https://pypi.python.org/packages/source/s/setuptools/setuptools-{version}.tar.gz'
    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = SetuptoolsRecipe()
