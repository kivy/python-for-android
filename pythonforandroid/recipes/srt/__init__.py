from pythonforandroid.recipe import PythonRecipe


class SrtRecipe(PythonRecipe):
    # srt only ships an sdist on PyPI (no wheel at all), which p4a's bulk
    # pip install of recipe-less requirements can't handle
    # (--only-binary=:all:). A minimal recipe routes it through the
    # normal setup.py install path instead. Needed as a real runtime
    # dependency: vosk/__init__.py does `import srt` unconditionally.
    name = "srt"
    version = "3.5.3"
    url = "https://pypi.python.org/packages/source/s/srt/srt-{version}.tar.gz"
    depends = ["setuptools"]
    call_hostpython_via_targetpython = False


recipe = SrtRecipe()
