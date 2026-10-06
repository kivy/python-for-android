from pythonforandroid.recipe import PythonRecipe


class WikipediaRecipe(PythonRecipe):
    # wikipedia only ships an sdist on PyPI (no wheel at all), which
    # p4a's bulk pip install of recipe-less requirements can't handle
    # (--only-binary=:all:). A minimal recipe routes it through the
    # normal setup.py install path instead.
    name = "wikipedia"
    version = "1.4.0"
    url = "https://pypi.python.org/packages/source/w/wikipedia/wikipedia-{version}.tar.gz"
    depends = ["setuptools", "beautifulsoup4", "requests"]
    call_hostpython_via_targetpython = False


recipe = WikipediaRecipe()
