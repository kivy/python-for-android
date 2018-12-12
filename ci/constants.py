from enum import Enum


class TargetPython(Enum):
    python2 = 0
    python3crystax = 1
    python3 = 2


# recipes that currently break the build
# a recipe could be broken for a target Python and not for the other,
# hence we're maintaining one list per Python target
BROKEN_RECIPES_PYTHON2 = set([
    # pythonhelpers.h:12:18: fatal error: string: No such file or directory
    'atom',
    # https://github.com/kivy/python-for-android/issues/550
    'audiostream',
    'brokenrecipe',
    # https://github.com/kivy/python-for-android/issues/1409
    'enaml',
    'evdev',
    # distutils.errors.DistutilsError
    # Could not find suitable distribution for Requirement.parse('cython')
    'ffpyplayer',
    'flask',
    'groestlcoin_hash',
    'hostpython3crystax',
    # https://github.com/kivy/python-for-android/issues/1398
    'ifaddrs',
    # https://github.com/kivy/python-for-android/issues/1354
    'kivent_core', 'kivent_cymunk', 'kivent_particles', 'kivent_polygen',
    'kiwisolver',
    # https://github.com/kivy/python-for-android/issues/1399
    'libglob',
    'libmysqlclient',
    'libsecp256k1',
    'libtribler',
    'ndghttpsclient',
    'm2crypto',
    'netifaces',
    'Pillow',
    # depends on cffi that still seems to have compilation issues
    'protobuf_cpp',
    'xeddsa',
    'x3dh',
    'pynacl',
    'doubleratchet',
    'omemo',
    'cryptography',
    # https://github.com/kivy/python-for-android/issues/1405
    'psycopg2',
    'pygame',
    # most likely some setup in the Docker container, because it works in host
    'pyjnius', 'pyopenal',
    'pyproj',
    'pysdl2',
    'pyzmq',
    'secp256k1',
    'shapely',
    'twisted',
    'vlc',
    'websocket-client',
    'zeroconf',
    'zope',
])
BROKEN_RECIPES_PYTHON3_CRYSTAX = set([
    'brokenrecipe',
    # enum34 is not compatible with Python 3.6 standard library
    # https://stackoverflow.com/a/45716067/185510
    'enum34',
    # https://github.com/kivy/python-for-android/issues/1398
    'ifaddrs',
    # https://github.com/kivy/python-for-android/issues/1399
    'libglob',
    # cannot find -lcrystax
    'cffi', 'pycryptodome', 'pymuk', 'secp256k1',
    # https://github.com/kivy/python-for-android/issues/1404
    'cryptography',
    # https://github.com/kivy/python-for-android/issues/1294
    'ffmpeg', 'ffpyplayer',
    # https://github.com/kivy/python-for-android/pull/1307 ?
    'gevent',
    'icu',
    # https://github.com/kivy/python-for-android/issues/1354
    'kivent_core', 'kivent_cymunk', 'kivent_particles', 'kivent_polygen',
    # https://github.com/kivy/python-for-android/issues/1405
    'libpq', 'psycopg2',
    'netifaces',
    # https://github.com/kivy/python-for-android/issues/1315 ?
    'opencv',
    'protobuf_cpp',
    # most likely some setup in the Docker container, because it works in host
    'pyjnius', 'pyopenal',
    # SyntaxError: invalid syntax (Python2)
    'storm',
    'vlc',
])
# to be created via https://github.com/kivy/python-for-android/issues/1514
BROKEN_RECIPES_PYTHON3 = set([
])

BROKEN_RECIPES = {
    TargetPython.python2: BROKEN_RECIPES_PYTHON2,
    TargetPython.python3crystax: BROKEN_RECIPES_PYTHON3_CRYSTAX,
    TargetPython.python3: BROKEN_RECIPES_PYTHON3,
}
# recipes that were already built will be skipped
CORE_RECIPES = set([
    'pyjnius', 'kivy', 'openssl', 'requests', 'sqlite3', 'setuptools',
    'numpy', 'android', 'python2', 'python3',
])
