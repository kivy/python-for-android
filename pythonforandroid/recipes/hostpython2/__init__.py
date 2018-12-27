from pythonforandroid.python import HostPythonRecipe


class Hostpython2Recipe(HostPythonRecipe):
    '''
    The hostpython2's recipe.

    .. versionchanged:: 0.6.0
        Updated to version 2.7.15 and the build process has been changed in
        favour of the recently added class
        :class:`~pythonforandroid.python.HostPythonRecipe`
    '''
    version = '2.7.15'
    name = 'hostpython2'
    conflicts = ['hostpython3', 'hostpython3crystax', 'hostpython2legacy']


recipe = Hostpython2Recipe()
