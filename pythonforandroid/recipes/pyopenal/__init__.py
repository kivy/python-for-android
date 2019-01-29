from pythonforandroid.recipe import PythonRecipe
from os.path import join


class PyOpenALRecipe(PythonRecipe):
    version = '0.7.3a1'
    url = 'https://files.pythonhosted.org/packages/source/p/pyopenal/PyOpenAL-{version}.tar.gz'
    depends = ['openal', 'numpy', 'setuptools']
    patches = [join('patches', 'fix-find-lib.patch')]

    call_hostpython_via_targetpython = False


recipe = PyOpenALRecipe()
