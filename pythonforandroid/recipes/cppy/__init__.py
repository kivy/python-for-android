from pythonforandroid.recipe import PythonRecipe


class CppyRecipe(PythonRecipe):
    site_packages_name = 'cppy'
    version = '1.1.0'
    url = 'https://github.com/nucleic/cppy/archive/{version}.zip'
    call_hostpython_via_targetpython = False
    # to be detected by the matplotlib install script
    install_in_hostpython = True
    depends = ['setuptools']


recipe = CppyRecipe()
