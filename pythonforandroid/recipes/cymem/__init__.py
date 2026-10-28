from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class CymemRecipe(CompiledComponentsPythonRecipe):
    version = "2.0.11"
    url = "https://pypi.python.org/packages/source/c/cymem/cymem-{version}.tar.gz"
    site_packages_name = "cymem"
    depends = [
        "setuptools",
        "cython",
    ]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = CymemRecipe()
