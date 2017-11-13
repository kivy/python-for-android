from pythonforandroid.toolchain import CompiledComponentsPythonRecipe


class UJsonRecipe(CompiledComponentsPythonRecipe):
    version = '1.35'
    url = 'https://pypi.python.org/packages/source/u/ujson/ujson-{version}.tar.gz'
    depends = [('python2', 'python3crystax')]
    
recipe = UJsonRecipe()
