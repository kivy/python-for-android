from pythonforandroid.recipe import PythonRecipe


class RuamelYamlRecipe(PythonRecipe):
    version = '0.15.77'
    url = 'https://pypi.python.org/packages/source/r/ruamel.yaml/ruamel.yaml-{version}.tar.gz'
    depends = ['setuptools']
    site_packages_name = 'ruamel'
    call_hostpython_via_targetpython = False
    patches = ['disable-pip-req.patch']


recipe = RuamelYamlRecipe()
