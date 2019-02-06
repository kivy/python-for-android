from pythonforandroid.recipe import PythonRecipe


class CherryPyRecipe(PythonRecipe):
    version = '5.1.0'
    url = 'https://bitbucket.org/cherrypy/cherrypy/get/{version}.tar.gz'
    depends = ['setuptools']
    site_packages_name = 'cherrypy'
    call_hostpython_via_targetpython = False


recipe = CherryPyRecipe()
