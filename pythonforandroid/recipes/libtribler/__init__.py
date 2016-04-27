from pythonforandroid.toolchain import PythonRecipe


class LibTriblerRecipe(PythonRecipe):

    version = 'devel'

    url = 'git+https://github.com/Tribler/tribler.git'

    depends = ['android', 'apsw', 'cherrypy', 'cryptography', 'decorator',
               'feedparser', 'ffmpeg', 'libnacl', 'libsodium', 'libtorrent',
               'm2crypto', 'netifaces', 'openssl', 'pyasn1', 'pil', 'pyleveldb',
               'python2', 'requests', 'twisted']

    site_packages_name = 'Tribler'


recipe = LibTriblerRecipe()