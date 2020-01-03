from pythonforandroid.recipe import PythonRecipe


class OmemoRecipe(PythonRecipe):
    name = 'omemo'
    version = '0.11.0'
    url = 'https://pypi.python.org/packages/source/O/OMEMO/OMEMO-{version}.tar.gz'
    site_packages_name = 'omemo'
    depends = [
        'setuptools',
        'x3dh',
        'cryptography',
    ]
    call_hostpython_via_targetpython = False


recipe = OmemoRecipe()
