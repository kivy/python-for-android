from pythonforandroid.recipe import PythonRecipe


class ThreadpoolctlRecipe(PythonRecipe):
    org = 'joblib'
    name = 'threadpoolctl'
    version = '2.1.0'
    url = f'https://github.com/{org}/{name}/archive/{version}.zip'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False
    patches = ['docstring.patch', 'setuptools.patch']


recipe = ThreadpoolctlRecipe()
