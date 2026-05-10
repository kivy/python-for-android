from pythonforandroid.recipe import PyProjectRecipe


class HttpxRecipe(PyProjectRecipe):
    name = "httpx"
    version = "0.28.1"
    url = (
        "https://pypi.python.org/packages/source/h/httpx/httpx-{version}.tar.gz"
    )
    depends = ["httpcore", "h11", "certifi", "idna", "sniffio"]


recipe = HttpxRecipe()
