from pythonforandroid.recipe import PythonRecipe


class SetuptoolsRecipe(PythonRecipe):
    version = '40.0.0'
    url = 'https://pypi.python.org/packages/source/s/setuptools/setuptools-{version}.zip'
    call_hostpython_via_targetpython = False
    install_in_hostpython = True
    depends = [('python2', 'python2legacy', 'python3', 'python3crystax')]
    # this recipe seems to control the dependency graph in some way, because
    # if removed the python2legacy recipe fails to solve the dependency order
    # when using the sdl2 bootstrap...so be careful removing this line!!!


recipe = SetuptoolsRecipe()
