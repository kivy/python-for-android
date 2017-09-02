from pythonforandroid.toolchain import PythonRecipe

class RequestsRecipe(PythonRecipe):
    version = '2.13.0'
    url = 'https://github.com/kennethreitz/requests/archive/v{version}.tar.gz'
    depends = ['hostpython2', 'setuptools']
    site_packages_name = 'requests'
    call_hostpython_via_targetpython = False

recipe = RequestsRecipe()
