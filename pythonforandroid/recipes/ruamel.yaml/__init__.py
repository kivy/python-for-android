from pythonforandroid.toolchain import PythonRecipe


class RuamelYamlRecipe(PythonRecipe):
    version = '0.14.5'
    url = 'https://pypi.python.org/packages/5c/13/c120a06b3add0f9763ca9190e5f6edb9faf9d34b158dd3cff7cc9097be03/ruamel.yaml-{version}.tar.gz'

    depends = [ ('python2', 'python3crystax') ]
    site_packages_name = 'ruamel'
    call_hostpython_via_targetpython = False

    patches = ['disable-pip-req.patch']

recipe = RuamelYamlRecipe()
