from pythonforandroid.toolchain import PythonRecipe


class PyYamlRecipe(PythonRecipe):
    version = "3.11"
    url = 'http://pyyaml.org/download/pyyaml/PyYAML-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), "setuptools"]
    site_packages_name = 'pyyaml'
    call_hostpython_via_targetpython = False

recipe = PyYamlRecipe()
