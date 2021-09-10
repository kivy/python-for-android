from pythonforandroid.recipe import PythonRecipe


class PydanticRecipe(PythonRecipe):
    version = '1.8.2'
    url = 'https://github.com/samuelcolvin/pydantic/archive/refs/tags/v{version}.zip'
    depends = ['setuptools']
    python_depends = ['Cython', 'devtools', 'email-validator', 'dataclasses', 'typing-extensions', 'python-dotenv']
    call_hostpython_via_targetpython = False


recipe = PydanticRecipe()
