import sh
from pythonforandroid.python import GuestPythonRecipe
from pythonforandroid.recipe import Recipe
from pythonforandroid.patching import version_starts_with


class Python3Recipe(GuestPythonRecipe):
    '''
    The python3's recipe
    ^^^^^^^^^^^^^^^^^^^^

    The python 3 recipe can be built with some extra python modules, but to do
    so, we need some libraries. By default, we ship the python3 recipe with
    some common libraries, defined in ``depends``. We also support some optional
    libraries, which are less common that the ones defined in ``depends``, so
    we added them as optional dependencies (``opt_depends``).

    Below you have a relationship between the python modules and the recipe
    libraries::

        - _ctypes: you must add the recipe for ``libffi``.
        - _sqlite3: you must add the recipe for ``sqlite3``.
        - _ssl: you must add the recipe for ``openssl``.
        - _bz2: you must add the recipe for ``libbz2`` (optional).
        - _lzma: you must add the recipe for ``liblzma`` (optional).

    .. note:: This recipe can be built only against API 21+.

    .. versionchanged:: 2019.10.06.post0
        Added optional dependencies: :mod:`~pythonforandroid.recipes.libbz2`
        and :mod:`~pythonforandroid.recipes.liblzma`
    .. versionchanged:: 0.6.0
        Refactored into class
        :class:`~pythonforandroid.python.GuestPythonRecipe`
    '''

    version = '3.8.1'
    url = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'
    name = 'python3'

    patches = [
        # Python 3.7.1
        ('patches/py3.7.1_fix-ctypes-util-find-library.patch', version_starts_with("3.7")),
        ('patches/py3.7.1_fix-zlib-version.patch', version_starts_with("3.7")),

        # Python 3.8.1
        ('patches/py3.8.1.patch', version_starts_with("3.8"))
    ]

    if sh.which('lld') is not None:
        patches = patches + [
            ("patches/py3.7.1_fix_cortex_a8.patch", version_starts_with("3.7")),
            ("patches/py3.8.1_fix_cortex_a8.patch", version_starts_with("3.8"))
        ]

    depends = ['hostpython3', 'sqlite3', 'openssl', 'libffi']
    # those optional depends allow us to build python compression modules:
    #   - _bz2.so
    #   - _lzma.so
    opt_depends = ['libbz2', 'liblzma']
    conflicts = ['python2']

    configure_args = (
        '--host={android_host}',
        '--build={android_build}',
        '--enable-shared',
        '--enable-ipv6',
        'ac_cv_file__dev_ptmx=yes',
        'ac_cv_file__dev_ptc=no',
        '--without-ensurepip',
        'ac_cv_little_endian_double=yes',
        '--prefix={prefix}',
        '--exec-prefix={exec_prefix}')

    def set_libs_flags(self, env, arch):
        env = super(Python3Recipe, self).set_libs_flags(env, arch)
        if 'openssl' in self.ctx.recipe_build_order:
            recipe = Recipe.get_recipe('openssl', self.ctx)
            self.configure_args += \
                ('--with-openssl=' + recipe.get_build_dir(arch.arch),)
        return env


recipe = Python3Recipe()
