from pythonforandroid.toolchain import PythonRecipe

class EnumCompatRecipe(PythonRecipe):
    version = "0.0.2"
    url = "https://pypi.python.org/packages/95/6e/26bdcba28b66126f66cf3e4cd03bcd63f7ae330d29ee68b1f6b623550bfa/enum-compat-{version}.tar.gz"

    call_hostpython_via_targetpython = False

recipe = EnumCompatRecipe()
