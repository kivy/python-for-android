from pythonforandroid.recipe import PythonRecipe


class LifxlanRecipe(PythonRecipe):
    name = "lifxlan"
    version = "1.2.9"
    url = "https://pypi.python.org/packages/source/l/lifxlan/lifxlan-{version}.tar.gz"
    depends = ["setuptools", "bitstring", "ifaddr"]
    call_hostpython_via_targetpython = False


recipe = LifxlanRecipe()
