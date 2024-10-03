from pythonforandroid.recipe import PythonRecipe


class JoblibRecipe(PythonRecipe):
    org = 'joblib'
    name = 'joblib'
    version = '0.17.0'
    url = f'https://github.com/{org}/{name}/archive/{version}.zip'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False
    patches = ['multiprocessing.patch']


recipe = JoblibRecipe()
