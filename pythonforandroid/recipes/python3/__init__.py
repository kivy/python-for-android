import sh
from pythonforandroid.python import GuestPythonRecipe
from pythonforandroid.recipe import Recipe
from pythonforandroid.patching import version_starts_with


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
