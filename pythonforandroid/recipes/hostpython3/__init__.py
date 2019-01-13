from pythonforandroid.python import HostPythonRecipe


class Hostpython3Recipe(HostPythonRecipe):
    '''
    The hostpython3's recipe.

    .. versionchanged:: 0.6.0
        Refactored into  the new class
        :class:`~pythonforandroid.python.HostPythonRecipe`
    '''
    version = '3.7.1'
    name = 'hostpython3'
    conflicts = ['hostpython2', 'hostpython3crystax']


recipe = Hostpython3Recipe()
