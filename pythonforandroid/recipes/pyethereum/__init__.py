from pythonforandroid.recipe import PythonRecipe


class PyethereumRecipe(PythonRecipe):
    version = 'v1.6.1'
    url = 'https://github.com/ethereum/pyethereum/archive/{version}.tar.gz'

    depends = [
        'setuptools', 'pycryptodome', 'pysha3', 'ethash', 'scrypt'
    ]

    call_hostpython_via_targetpython = False


recipe = PyethereumRecipe()
