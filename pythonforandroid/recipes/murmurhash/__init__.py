from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class MurmurhashRecipe(CompiledComponentsPythonRecipe):
    version = "1.0.13"
    url = "https://pypi.python.org/packages/source/m/murmurhash/murmurhash-{version}.tar.gz"
    site_packages_name = "murmurhash"
    depends = [
        "setuptools",
        "cython",
    ]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = MurmurhashRecipe()
