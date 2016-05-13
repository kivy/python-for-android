from pythonforandroid.toolchain import CompiledComponentsPythonRecipe


class GeventRecipe(CompiledComponentsPythonRecipe):
    version = '1.1.1'
    url = 'https://pypi.python.org/packages/source/g/gevent/gevent-{version}.tar.gz'
    depends = [('python2', 'python3crystax'), 'greenlet']
    patches = ["gevent.patch"]

recipe = GeventRecipe()
