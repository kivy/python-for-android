from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class RegexRecipe(CompiledComponentsPythonRecipe):
    name = 'regex'
    version = '2017.07.28'
    url = 'https://pypi.python.org/packages/d1/23/5fa829706ee1d4452552eb32e0bfc1039553e01f50a8754c6f7152e85c1b/regex-{version}.tar.gz'

    depends = ['setuptools']


recipe = RegexRecipe()
