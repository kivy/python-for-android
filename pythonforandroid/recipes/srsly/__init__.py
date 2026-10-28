from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class SrslyRecipe(CompiledComponentsPythonRecipe):
    version = "2.5.1"
    url = "https://pypi.python.org/packages/source/s/srsly/srsly-{version}.tar.gz"
    site_packages_name = "srsly"
    depends = [
        "setuptools",
        "cython",
        "catalogue",
    ]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = SrslyRecipe()
