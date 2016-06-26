from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe

class EnamlRecipe(CppCompiledComponentsPythonRecipe):
    site_packages_name = 'enaml'
    version = '0.9.8'
    url = 'https://github.com/nucleic/enaml/archive/master.zip'
    patches = ['0001-Update-setup.py.patch'] # Remove PyQt dependency
    depends = ['python2','setuptools','atom','kiwisolver']

recipe = EnamlRecipe()
