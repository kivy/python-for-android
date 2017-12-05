from pythonforandroid.toolchain import PythonRecipe

class DecoratorPyRecipe(PythonRecipe):
    version = '4.0.9'
    url = 'https://pypi.python.org/packages/source/d/decorator/decorator-{version}.tar.gz'
    depends = ['hostpython2', 'setuptools']
    site_packages_name = 'decorator'
    call_hostpython_via_targetpython = False

recipe = DecoratorPyRecipe()
