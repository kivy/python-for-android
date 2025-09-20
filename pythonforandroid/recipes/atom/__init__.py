from pythonforandroid.recipe import PyProjectRecipe


class AtomRecipe(PyProjectRecipe):
    site_packages_name = "atom"
    version = "0.11.0"
    url = "https://files.pythonhosted.org/packages/source/a/atom/atom-{version}.tar.gz"
    depends = ["setuptools"]
    patches = ["pyproject.toml.patch"]


recipe = AtomRecipe()
