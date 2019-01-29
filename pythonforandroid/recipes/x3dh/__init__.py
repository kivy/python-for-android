from pythonforandroid.recipe import PythonRecipe


class X3DHRecipe(PythonRecipe):
    name = 'x3dh'
    version = '0.5.3'
    url = 'https://pypi.python.org/packages/source/X/X3DH/X3DH-{version}.tar.gz'
    site_packages_name = 'x3dh'
    depends = [
        'setuptools',
        'cryptography',
        'xeddsa',
    ]
    patches = ['requires_fix.patch']
    call_hostpython_via_targetpython = False


recipe = X3DHRecipe()
