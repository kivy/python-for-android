FAQ
===

arm-linux-androideabi-gcc: Internal error: Killed (program cc1)
---------------------------------------------------------------

This could happen if you are not using a validated SDK/NDK with Python for
Android. Go to :doc:`prerequisites.rst` to see which one are working.

_sqlite3.so not found
---------------------

We recently fixed sqlite3 compilation. In case of, you must:

* Install development headers for sqlite3 if it's not already installed. On Ubuntu:

    apt-get install libsqlite3-dev

* Compile the distribution with (sqlite3 must be the first argument)::

    ./distribute.sh -m 'sqlite3 kivy'

* Go into your distribution at `dist/default`
* Edit blacklist.txt, and remove all the lines concerning sqlite3::

    sqlite3/*
    lib-dynload/_sqlite3.so

And then, sqlite3 will be compiled, and included in your APK.
