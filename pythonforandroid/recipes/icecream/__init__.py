from pythonforandroid.recipe import PythonRecipe


class IcecreamRecipe(PythonRecipe):
    version = '2.1.1'
    url = 'https://github.com/gruns/icecream/archive/refs/tags/v{version}.tar.gz'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False


recipe = IcecreamRecipe()
