from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class GitPythonRecipe(CompiledComponentsPythonRecipe):
    version = '20.1.0'
    url = 'git+https://github.com/gitpython-developers/GitPython'
    depends = ['gitdb', 'typing-extensions']
    call_hostpython_via_targetpython = False
    build_cmd = 'build'


recipe = GitPythonRecipe()
