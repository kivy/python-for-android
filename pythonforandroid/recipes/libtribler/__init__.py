from pythonforandroid.toolchain import PythonRecipe

"""
Privacy with BitTorrent and resilient to shut down

http://www.tribler.org
"""
class LibTriblerRecipe(PythonRecipe):

    version = 'devel'

    url = 'git+https://github.com/Tribler/tribler.git'

    depends = ['apsw', 'cryptography', 'ffmpeg', 'libsodium', 'libtorrent', 'm2crypto',
               'netifaces', 'openssl', 'pil', 'pycrypto', 'pyleveldb', 'python2', 'twisted',
              ]

    python_depends = ['chardet', 'cherrypy', 'configobj', 'decorator', 'feedparser',
                      'libnacl', 'pyasn1', 'requests', 'six',
                     ]

    site_packages_name = 'Tribler'


recipe = LibTriblerRecipe()