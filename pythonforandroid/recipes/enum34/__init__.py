
from pythonforandroid.toolchain import PythonRecipe


class Enum34Recipe(PythonRecipe):
    version = '1.0.4'
    url = 'https://pypi.python.org/packages/source/e/enum34/enum34-{version}.tar.gz'
    depends = ['python2']
    site_packages_name = 'enum'

recipe = Enum34Recipe()
