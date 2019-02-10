from pythonforandroid.recipe import PythonRecipe

"""
Privacy with BitTorrent and resilient to shut down

http://www.tribler.org
"""


class LibTriblerRecipe(PythonRecipe):

    version = 'devel'

    url = 'git+https://github.com/Tribler/tribler.git'

    depends = ['apsw', 'cryptography', 'ffmpeg', 'libsodium', 'libtorrent', 'm2crypto',
               'netifaces', 'openssl', 'pil', 'pycrypto', 'pyleveldb', 'twisted',
              ]

    conflicts = ['python3']

    python_depends = ['chardet', 'cherrypy', 'configobj', 'decorator', 'feedparser',
                      'libnacl', 'pyasn1', 'requests', 'six',
                     ]

    site_packages_name = 'Tribler'


recipe = LibTriblerRecipe()
