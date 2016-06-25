from pythonforandroid.recipe import CppCompiledComponentsPythonRecipe

class EnamlRecipe(CppCompiledComponentsPythonRecipe):
    site_packages_name = 'enaml'
    call_hostpython_via_targetpython = False
    version = '0.9.8'
    url = 'https://github.com/frmdstryr/enaml/archive/master.zip'
    depends = ['python2']

recipe = EnamlRecipe()