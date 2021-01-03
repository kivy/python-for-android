from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class Argon2Recipe(CompiledComponentsPythonRecipe):
    version = '20.1.0'
    url = 'url = 'git+https://github.com/hynek/argon2-cffi@{version}'
    depends = ['setuptools', 'cffi']
    call_hostpython_via_targetpython = False


recipe = Argon2Recipe()
