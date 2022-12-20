from pythonforandroid.recipe import PythonRecipe


class SemanticVersionRecipe(PythonRecipe):
    version = '2.10.0'
    url = 'https://pypi.python.org/packages/source/s/semantic-version/semantic_version-{version}.tar.gz'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = SemanticVersionRecipe()
