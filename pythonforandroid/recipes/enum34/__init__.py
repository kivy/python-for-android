from pythonforandroid.toolchain import PythonRecipe

class Enum34Recipe(PythonRecipe):
    version = '1.1.6'
    url = 'https://pypi.python.org/packages/bf/3e/31d502c25302814a7c2f1d3959d2a3b3f78e509002ba91aea64993936876/enum34-1.1.6.tar.gz#md5=5f13a0841a61f7fc295c514490d120d0'
    depends = ['python2', 'setuptools']
    site_packages_name = 'enum'
    call_hostpython_via_targetpython = False

recipe = Enum34Recipe()
