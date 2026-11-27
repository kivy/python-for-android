from pythonforandroid.recipe import PyProjectRecipe


class MpvRecipe(PyProjectRecipe):
    name = "mpv"
    version = "1.0.8"
    url = "https://pypi.io/packages/source/p/python-mpv/python_mpv-{version}.tar.gz"
    depends = ["python3", "libmpv"]
    patches = ["android.patch"]


recipe = MpvRecipe()
