from pythonforandroid.recipe import PythonRecipe


class PyethereumRecipe(PythonRecipe):

    url = 'https://github.com/ethereum/pyethereum/archive/develop.zip'

    depends = [
        'python2', 'setuptools', 'pycryptodome', 'pysha3', 'ethash', 'scrypt'
    ]

    call_hostpython_via_targetpython = False


recipe = PyethereumRecipe()
