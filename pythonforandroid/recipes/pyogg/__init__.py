from pythonforandroid.recipe import PythonRecipe
from os.path import join


class PyOggRecipe(PythonRecipe):
    version = '0.6.4a1'
    url = 'https://files.pythonhosted.org/packages/source/p/pyogg/PyOgg-{version}.tar.gz'
    depends = ['libogg', 'libvorbis', 'setuptools']
    patches = [join('patches', 'fix-find-lib.patch')]

    call_hostpython_via_targetpython = False


recipe = PyOggRecipe()
