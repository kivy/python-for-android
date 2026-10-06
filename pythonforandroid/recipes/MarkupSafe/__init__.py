from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class MarkupSafeRecipe(CompiledComponentsPythonRecipe):
    version = "2.1.5"
    url = "https://pypi.python.org/packages/source/M/MarkupSafe/MarkupSafe-{version}.tar.gz"
    depends = [
        "setuptools",
        "cython",
        "pyparsing",
    ]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = MarkupSafeRecipe()
