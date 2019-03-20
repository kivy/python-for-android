import sh
from pythonforandroid.python import GuestPythonRecipe
from pythonforandroid.recipe import Recipe


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

    patches = ["patches/fix-ctypes-util-find-library.patch"]

    if sh.which('lld') is not None:
        patches = patches + ["patches/remove-fix-cortex-a8.patch"]

    depends = ['hostpython3', 'sqlite3', 'openssl', 'libffi']
    conflicts = ['python3crystax', 'python2', 'python2legacy']

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

    def set_libs_flags(self, env, arch):
        env = super(Python3Recipe, self).set_libs_flags(env, arch)
        if 'openssl' in self.ctx.recipe_build_order:
            recipe = Recipe.get_recipe('openssl', self.ctx)
            self.configure_args += \
                ('--with-openssl=' + recipe.get_build_dir(arch.arch),)
        return env


recipe = Python3Recipe()
