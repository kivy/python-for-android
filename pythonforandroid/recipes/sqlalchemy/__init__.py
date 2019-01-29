from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class SQLAlchemyRecipe(CompiledComponentsPythonRecipe):
    name = 'sqlalchemy'
    version = '1.0.9'
    url = 'https://pypi.python.org/packages/source/S/SQLAlchemy/SQLAlchemy-{version}.tar.gz'

    depends = ['setuptools']

    patches = ['zipsafe.patch']


recipe = SQLAlchemyRecipe()
