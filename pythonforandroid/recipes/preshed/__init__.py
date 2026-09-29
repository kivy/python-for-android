from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class PreshedRecipe(CompiledComponentsPythonRecipe):
    version = "3.0.10"
    url = "https://pypi.python.org/packages/source/p/preshed/preshed-{version}.tar.gz"
    site_packages_name = "preshed"
    depends = [
        "setuptools",
        "cython",
        "cymem",
        "murmurhash",
    ]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = PreshedRecipe()
