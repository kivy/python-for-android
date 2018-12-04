from pythonforandroid.python import GuestPythonRecipe


class Python3Recipe(GuestPythonRecipe):
    '''
    The python3's recipe.

    .. note:: This recipe can be built only against API 21+. Also, in order to
        build certain python modules, we need to add some extra recipes to our
        build requirements:

            - ctypes: you must add the recipe for ``libffi``.

    .. versionchanged:: 0.6.0
        Refactored into class
        :class:`~pythonforandroid.python.GuestPythonRecipe`
    '''

    version = '3.7.1'
    url = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'
    name = 'python3'

    depends = ['hostpython3']
    conflicts = ['python3crystax', 'python2']

    configure_args = (
        '--host={android_host}',
        '--build={android_build}',
        '--enable-shared',
        '--disable-ipv6',
        'ac_cv_file__dev_ptmx=yes',
        'ac_cv_file__dev_ptc=no',
        '--without-ensurepip',
        'ac_cv_little_endian_double=yes',
        '--prefix={prefix}',
        '--exec-prefix={exec_prefix}')


recipe = Python3Recipe()
