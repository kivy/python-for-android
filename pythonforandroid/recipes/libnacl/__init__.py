from pythonforandroid.toolchain import PythonRecipe

class LibNaClRecipe(PythonRecipe):
    version = '1.4.4'
    url = 'https://github.com/saltstack/libnacl/archive/v{version}.tar.gz'
    depends = ['hostpython2', 'setuptools']
    site_packages_name = 'libnacl'
    call_hostpython_via_targetpython = False

recipe = LibNaClRecipe()
