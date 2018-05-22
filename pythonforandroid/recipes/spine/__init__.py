from pythonforandroid.recipe import CythonRecipe


class SpineCython(CythonRecipe):

    version = '0.5.1'
    url = 'https://github.com/tileworks/spine-cython/archive/{version}.zip'
    name = 'spine'
    depends = ['setuptools']
    site_packages_name = 'spine'
    call_hostpython_via_targetpython = False


recipe = SpineCython()
