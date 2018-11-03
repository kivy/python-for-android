from pythonforandroid.recipe import PythonRecipe


class OmemoRecipe(PythonRecipe):
    name = 'omemo'
    version = '0.7.1'
    url = 'https://pypi.python.org/packages/source/O/OMEMO/OMEMO-{version}.tar.gz'
    site_packages_name = 'omemo'
    depends = [
        ('python2', 'python3crystax'),
        'setuptools',
        'protobuf_cpp',
        'x3dh',
        'DoubleRatchet',
        'hkdf==0.0.3',
    ]
    patches = ['remove_dependencies.patch', 'wireformat.patch']
    call_hostpython_via_targetpython = False


recipe = OmemoRecipe()
