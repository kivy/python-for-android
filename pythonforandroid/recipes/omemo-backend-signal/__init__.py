from pythonforandroid.recipe import PythonRecipe


class OmemoBackendSignalRecipe(PythonRecipe):
    name = 'omemo-backend-signal'
    version = '0.2.5'
    url = 'https://pypi.python.org/packages/source/o/omemo-backend-signal/omemo-backend-signal-{version}.tar.gz'
    site_packages_name = 'omemo-backend-signal'
    depends = [
        'setuptools',
        'protobuf_cpp',
        'x3dh',
        'DoubleRatchet',
        'hkdf==0.0.3',
        'cryptography',
        'omemo',
    ]
    call_hostpython_via_targetpython = False


recipe = OmemoBackendSignalRecipe()
