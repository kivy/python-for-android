
from pythonforandroid.recipe import PythonRecipe


class MplfinanceRecipe(PythonRecipe):

    # there is not an official release yet...
    # so pinned to last commit at the time of writing
    version = 'cde5008'
    url = 'https://github.com/matplotlib/mplfinance/archive/{version}.zip'

    depends = ['setuptools', 'matplotlib', 'pandas']
    conflicts = ['python2']

    call_hostpython_via_targetpython = False


recipe = MplfinanceRecipe()
