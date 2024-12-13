from pythonforandroid.recipe import PyProjectRecipe


class SQLAlchemyRecipe(PyProjectRecipe):
    name = 'sqlalchemy'
    version = '2.0.30'
    url = 'https://github.com/sqlalchemy/sqlalchemy/archive/refs/tags/rel_{}.tar.gz'
    depends = ['setuptools']

    @property
    def versioned_url(self):
        return self.url.format(self.version.replace(".", "_"))


recipe = SQLAlchemyRecipe()
