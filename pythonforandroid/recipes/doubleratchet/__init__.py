from pythonforandroid.recipe import PythonRecipe


class DoubleRatchetRecipe(PythonRecipe):
    name = 'doubleratchet'
    version = '0.4.0'
    url = 'https://pypi.python.org/packages/source/D/DoubleRatchet/DoubleRatchet-{version}.tar.gz'
    depends = [
        ('python2', 'python3crystax'),
        'setuptools',
        'cryptography',
    ]
    patches = ['requires_fix.patch']
    call_hostpython_via_targetpython = False


recipe = DoubleRatchetRecipe()
