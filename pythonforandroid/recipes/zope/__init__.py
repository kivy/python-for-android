from pythonforandroid.toolchain import PythonRecipe

class ZopeRecipe(PythonRecipe):
    name = 'zope'
    version = '4.1.2'
    url = 'http://pypi.python.org/packages/source/z/zope.interface/zope.interface-{version}.tar.gz'
    depends = ['python2']
    call_hostpython_via_targetpython = False

recipe = ZopeRecipe()
