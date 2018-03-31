from pythonforandroid.toolchain import PythonRecipe


class SetuptoolsRecipe(PythonRecipe):
    version = '18.3.1'
    url = 'https://pypi.python.org/packages/source/s/setuptools/setuptools-{version}.tar.gz'

    depends = [('python2', 'python3crystax')]

    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = SetuptoolsRecipe()
