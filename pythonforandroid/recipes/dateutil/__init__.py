from pythonforandroid.recipe import PythonRecipe


class DateutilRecipe(PythonRecipe):
    name = 'dateutil'
    version = '2.6.0'
    url = 'https://pypi.python.org/packages/51/fc/39a3fbde6864942e8bb24c93663734b74e281b984d1b8c4f95d64b0c21f6/python-dateutil-2.6.0.tar.gz'

    depends = ["setuptools"]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = DateutilRecipe()
