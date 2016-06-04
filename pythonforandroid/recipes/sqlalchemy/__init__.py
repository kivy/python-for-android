
from pythonforandroid.toolchain import CompiledComponentsPythonRecipe


class SQLAlchemyRecipe(CompiledComponentsPythonRecipe):
    name = 'sqlalchemy'
    version = '1.0.9'
    url = 'https://pypi.python.org/packages/source/S/SQLAlchemy/SQLAlchemy-{version}.tar.gz'
    
    depends = [('python2', 'python3'), 'setuptools', 'wheel']
    
    patches = ['zipsafe.patch']

    call_hostpython_via_targetpython = False
    use_pip = True
    wheel_name = 'SQLAlchemy'


recipe = SQLAlchemyRecipe()
