from pythonforandroid.recipe import PythonRecipe


class PydanticRecipe(PythonRecipe):
    version = '1.8.2'
    url = 'https://github.com/samuelcolvin/pydantic.git'
    depends = ['setuptools']
    python_depends = ['Cython==0.29.23', 'devtools==0.6.1', 'email-validator==1.1.2','dataclasses==0.6', 'typing-extensions==3.10.0.0', 'python-dotenv==0.17.1']
    call_hostpython_via_targetpython = False


recipe = PydanticRecipe()
