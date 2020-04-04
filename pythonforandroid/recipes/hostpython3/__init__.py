from pythonforandroid.python import HostPythonRecipe


class Hostpython3Recipe(HostPythonRecipe):
    '''
    The hostpython3's recipe.

    .. versionchanged:: 0.6.0
        Refactored into  the new class
        :class:`~pythonforandroid.python.HostPythonRecipe`
    '''
    version = '3.8.1'
    name = 'hostpython3'
    conflicts = ['hostpython2']


recipe = Hostpython3Recipe()
