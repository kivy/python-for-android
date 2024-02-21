from pythonforandroid.recipe import CompiledComponentsPythonRecipe

class MySQLConnectorPythonRecipe(CompiledComponentsPythonRecipe):

    
    name = 'mysql-connector-python'
    version = '8.3.0'
    url = f'https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-{version}.tar.gz'
    call_hostpython_via_targetpython = False

    depends = ['python3','setuptools']

recipe = MySQLConnectorPythonRecipe()