FAQ
===

arm-linux-androideabi-gcc: Internal error: Killed (program cc1)
---------------------------------------------------------------

This could happen if you are not using a validated SDK/NDK with Python for
Android. Go to :doc:`prerequisites` to see which one are working.

_sqlite3.so not found
---------------------

We recently fixed sqlite3 compilation. In case of this error, you
must:

* Install development headers for sqlite3 if they are not already
  installed. On Ubuntu:

    apt-get install libsqlite3-dev

* Compile the distribution with (sqlite3 must be the first argument)::

    ./distribute.sh -m 'sqlite3 kivy'

* Go into your distribution at `dist/default`
* Edit blacklist.txt, and remove all the lines concerning sqlite3::

    sqlite3/*
    lib-dynload/_sqlite3.so

Then sqlite3 will be compiled and included in your APK.

Too many levels of symbolic links
-----------------------------------------------------

Python for Android does not work within a virtual enviroment. The Python for 
Android directory must be outside of the virtual enviroment prior to running

    ./distribute.sh -m "kivy"

or else you may encounter OSError: [Errno 40] Too many levels of symbolic links.