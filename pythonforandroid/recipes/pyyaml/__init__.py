from pythonforandroid.recipe import PythonRecipe


class PyYamlRecipe(PythonRecipe):
    version = "3.12"
    url = 'http://pyyaml.org/download/pyyaml/PyYAML-{version}.tar.gz'
    depends = ["setuptools"]
    site_packages_name = 'pyyaml'


recipe = PyYamlRecipe()
