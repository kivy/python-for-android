from pythonforandroid.recipe import PythonRecipe


class CppyRecipe(PythonRecipe):
    site_packages_name = 'cppy'

    # Pin to commit: `Nucleic migration and project documentation`,
    # because the official releases are too old, at time of writing
    version = '4e0b956'
    url = 'https://github.com/nucleic/cppy/archive/{version}.zip'
    call_hostpython_via_targetpython = False
    # to be detected by the matplotlib install script
    install_in_hostpython = True
    depends = ['setuptools']


recipe = CppyRecipe()
