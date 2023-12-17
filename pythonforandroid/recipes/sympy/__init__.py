
from pythonforandroid.recipe import PythonRecipe


class SympyRecipe(PythonRecipe):
    version = '1.1.1'
    url = 'https://github.com/sympy/sympy/releases/download/sympy-{version}/sympy-{version}.tar.gz'

    depends = ['mpmath']

    patches = ['fix_timeutils.patch', 'fix_pretty_print.patch']


recipe = SympyRecipe()
