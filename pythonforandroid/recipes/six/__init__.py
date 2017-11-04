
from pythonforandroid.toolchain import PythonRecipe


class SixRecipe(PythonRecipe):
    version = '1.11.0'
    url = 'https://pypi.python.org/packages/16/d8/bc6316cf98419719bd59c91742194c111b6f2e85abac88e496adefaf7afe/six-1.11.0.tar.gz#md5=d12789f9baf7e9fb2524c0c64f1773f8'
    depends = [('python2', 'python3crystax')]

recipe = SixRecipe()
