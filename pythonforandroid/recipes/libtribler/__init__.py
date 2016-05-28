from pythonforandroid.toolchain import PythonRecipe

"""
Privacy with BitTorrent and resilient to shut down

http://www.tribler.org
"""
class LibTriblerRecipe(PythonRecipe):

    version = 'devel'

    url = 'git+https://github.com/Tribler/tribler.git'

    depends = ['apsw', 'cherrypy', 'cryptography', 'decorator', 'feedparser',
               'ffmpeg', 'libnacl', 'libsodium', 'libtorrent', 'm2crypto',
               'netifaces', 'openssl', 'pyasn1', 'pil', 'pycrypto', 'pyleveldb',
               'python2', 'requests', 'six', 'twisted']

    site_packages_name = 'Tribler'


recipe = LibTriblerRecipe()