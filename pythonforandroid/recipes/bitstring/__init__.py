from pythonforandroid.recipe import PythonRecipe


class BitstringRecipe(PythonRecipe):
    name = "bitstring"
    version = "3.1.9"
    url = "https://pypi.python.org/packages/source/b/bitstring/bitstring-{version}.tar.gz"
    depends = ["setuptools"]
    call_hostpython_via_targetpython = False


recipe = BitstringRecipe()
