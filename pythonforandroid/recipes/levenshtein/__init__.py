from pythonforandroid.toolchain import CompiledComponentsPythonRecipe


class LevenshteinRecipe(CompiledComponentsPythonRecipe):
    name="levenshtein"
    version = '0.12.0'
    url = 'https://pypi.python.org/packages/source/p/python-Levenshtein/python-Levenshtein-{version}.tar.gz'
    depends = [('python2', 'python3'), 'setuptools']

    call_hostpython_via_targetpython = False
    install_in_targetpython = False
    install_in_hostpython = True

recipe = LevenshteinRecipe()
