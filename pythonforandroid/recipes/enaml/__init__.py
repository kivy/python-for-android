from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe

class EnamlRecipe(CppCompiledComponentsPythonRecipe):
    site_packages_name = 'enaml'
    version = '0.9.8'
    url = 'https://github.com/frmdstryr/enaml/archive/master.zip'
    depends = ['python2','setuptools','atom','kiwisolver']

recipe = EnamlRecipe()