from pythonforandroid.recipe import PythonRecipe


class PydanticRecipe(PythonRecipe):
    version = '1.10.4'
    url = 'https://github.com/pydantic/pydantic/archive/refs/tags/v{version}.zip'
    depends = ['setuptools']
    python_depends = ['Cython', 'devtools', 'email-validator', 'typing-extensions', 'python-dotenv']
    call_hostpython_via_targetpython = False


recipe = PydanticRecipe()
