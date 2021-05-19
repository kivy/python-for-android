from pythonforandroid.recipe import CompiledComponentsPythonRecipe


class GitPythonRecipe(CompiledComponentsPythonRecipe):
    version = '3.1.17'
    url = 'https://github.com/gitpython-developers/GitPython/archive/{version}.zip'
    depends = ['setuptools']
    python_depends = ['gitdb', 'typing-extensions']
    call_hostpython_via_targetpython = False


recipe = GitPythonRecipe()
