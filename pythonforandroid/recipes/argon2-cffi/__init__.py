from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class Argon2Recipe(CompiledComponentsPythonRecipe):
    version = '20.1.0'
    url = 'git+https://github.com/hynek/argon2-cffi'
    depends = ['setuptools', 'cffi']
    call_hostpython_via_targetpython = False
    build_cmd = 'build'


recipe = Argon2Recipe()
