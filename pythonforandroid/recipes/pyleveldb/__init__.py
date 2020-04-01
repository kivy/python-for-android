from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe


class PyLevelDBRecipe(CppCompiledComponentsPythonRecipe):
    version = '0.193'
    url = 'https://pypi.python.org/packages/source/l/leveldb/leveldb-{version}.tar.gz'
    depends = ['snappy', 'leveldb', ('hostpython2', 'hostpython3'), 'setuptools']
    patches = ['bindings-only.patch']
    call_hostpython_via_targetpython = False  # Due to setuptools
    site_packages_name = 'leveldb'


recipe = PyLevelDBRecipe()
