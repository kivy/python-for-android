from enum import Enum


class TargetPython(Enum):
    python3 = 2


# recipes that currently break the build
# a recipe could be broken for a target Python and not for the other,
# hence we're maintaining one list per Python target
BROKEN_RECIPES_PYTHON3 = set([
    'brokenrecipe',
    # enum34 is not compatible with Python 3.6 standard library
    # https://stackoverflow.com/a/45716067/185510
    'enum34',
    # build_dir = glob.glob('build/lib.*')[0]
    # IndexError: list index out of range
    'secp256k1',
    'ffpyplayer',
    # requires `libpq-dev` system dependency e.g. for `pg_config` binary
    'psycopg2',
    # most likely some setup in the Docker container, because it works in host
    'pyjnius', 'pyopenal',
    # SyntaxError: invalid syntax (Python2)
    'storm',
    # mpmath package with a version >= 0.19 required
    'sympy',
    'vlc',
    # need extra gfortran NDK system add-on
    'lapack', 'scipy',
    # Outdated and there's a chance that is now useless.
    'zope_interface',
    # Requires zope_interface, which is broken.
    'twisted',
    # genericndkbuild is incompatible with sdl2 (which is build by default when targeting sdl2 bootstrap)
    'genericndkbuild',
])

BROKEN_RECIPES = {
    TargetPython.python3: BROKEN_RECIPES_PYTHON3,
}
# recipes that were already built will be skipped
CORE_RECIPES = set([
    'pyjnius', 'kivy', 'openssl', 'requests', 'sqlite3', 'setuptools',
    'numpy', 'android', 'hostpython3', 'python3',
])
