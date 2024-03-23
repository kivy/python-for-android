from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class MySQLConnectorPythonRecipe(CompiledComponentsPythonRecipe):

    name = 'mysql-connector-python'
    version = '8.3.0'
    url = (
        f"https://downloads.mysql.com/archives/get/p/29/file/"
        f"mysql-connector-python-py{version}-1ubuntu23.10_amd64.deb"
    )
    call_hostpython_via_targetpython = False

    depends = ['python3', 'setuptools']


recipe = MySQLConnectorPythonRecipe()
