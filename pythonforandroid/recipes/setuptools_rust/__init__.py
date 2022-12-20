from pythonforandroid.recipe import PythonRecipe


class SetuptoolsRustRecipe(PythonRecipe):
    version = '1.2.0'
    url = 'https://pypi.python.org/packages/source/s/setuptools-rust/setuptools-rust-{version}.tar.gz'
    depends = ['typing_extensions', 'semantic_version']
    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = SetuptoolsRustRecipe()
