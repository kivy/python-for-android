from pythonforandroid.python import GuestPythonRecipe
# from pythonforandroid.patching import is_api_lt


class Python2Recipe(GuestPythonRecipe):
    '''
    The python2's recipe.

    .. note:: This recipe can be built only against API 21+

    .. versionchanged:: 0.6.0
        Updated to version 2.7.15 and the build process has been changed in
        favour of the recently added class
        :class:`~pythonforandroid.python.GuestPythonRecipe`
    '''
    version = "2.7.15"
    url = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'
    name = 'python2'

    depends = ['hostpython2']
    conflicts = ['python3crystax', 'python3']

    patches = [
               # new 2.7.15 patches
               # ('patches/fix-api-minor-than-21.patch',
               #  is_api_lt(21)), # Todo: this should be tested
               'patches/fix-missing-extensions.patch',
               'patches/fix-filesystem-default-encoding.patch',
               'patches/fix-locale.patch',
               'patches/fix-init-site.patch',
               ]

    configure_args = ('--host={android_host}',
                      '--build={android_build}',
                      '--enable-shared',
                      '--disable-ipv6',
                      '--disable-toolbox-glue',
                      '--disable-framework',
                      'ac_cv_file__dev_ptmx=yes',
                      'ac_cv_file__dev_ptc=no',
                      '--without-ensurepip',
                      'ac_cv_little_endian_double=yes',
                      'ac_cv_header_langinfo_h=no',
                      '--prefix={prefix}',
                      '--exec-prefix={exec_prefix}')


recipe = Python2Recipe()
