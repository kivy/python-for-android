from pythonforandroid.recipe import CompiledComponentsPythonRecipe

class Argon2Recipe(CompiledComponentsPythonRecipe):
    version = '20.1.0'
    url = 'https://github.com/hynek/argon2-cffi/archive/master.zip'
    depends = ['cffi']
    call_hostpython_via_targetpython = False

recipe = Argon2Recipe()
