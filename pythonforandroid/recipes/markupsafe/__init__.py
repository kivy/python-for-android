from pythonforandroid.recipe import PyProjectRecipe


class MarkupsafeRecipe(PyProjectRecipe):
    version = "3.0.3"
    hash = "7e/99/7690b6d4034fffd95959cbe0c02de8deb3098cc577c67bb6a24fe5d7caa7"
    url = (
        "https://files.pythonhosted.org/packages/"
        + hash
        + "/markupsafe-{version}.tar.gz"
    )


recipe = MarkupsafeRecipe()
