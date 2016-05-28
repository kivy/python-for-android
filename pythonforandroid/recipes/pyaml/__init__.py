from pythonforandroid.toolchain import PythonRecipe


class PyamlRecipe(PythonRecipe):
    version = "15.8.2"
    url = 'https://pypi.python.org/packages/source/p/pyaml/pyaml-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), "setuptools"]
    site_packages_name = 'yaml'
    call_hostpython_via_targetpython = False

recipe = PyamlRecipe()
