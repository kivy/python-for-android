
Build options
=============

This page contains instructions for using some of the specific python-for-android build options.


Python version
--------------

python-for-android now supports building APKs with either python2 or
python3, but these have extra requirements or potential disadvantages
as below.


python2
~~~~~~~

Select this by adding it in your requirements, e.g. ``--requirements=python2``.

This option builds Python 2.7.2 for your selected Android
architecture. There are no special requirements, all the building is
done locally.

The python2 build is also the way python-for-android originally
worked, even in the old toolchain.


python3
~~~~~~~

.. warning::
   Python3 support is experimental, and some of these details
   may change as it is improved and fully stabilised.

.. note:: You must manually download the `CrystaX NDK
   <https://www.crystax.net/android/ndk>`__ and tell
   python-for-android to use it with ``--ndk-dir /path/to/NDK``.

Select this by adding the ``python3crystax`` recipe to your
requirements, e.g. ``--requirements=python3crystax``.

This uses the prebuilt Python from the `CrystaX NDK
<https://www.crystax.net/android/ndk>`__, a drop-in replacement for
Google's official NDK which includes many improvements. You
*must* use the CrystaX NDK 10.3.0 or higher when building with
python3. You can get it `here
<https://www.crystax.net/en/download>`__.

The python3crystax build is is handled quite differently to python2 so
there may be bugs or surprising behaviours. If you come across any,
feel free to `open an issue
<https://github.com/kivy/python-for-android>`__.

As this build is experimental, some features are missing and
the build is not fully optimised so APKs are probably a little larger
and slower than they need to be. This is currently being addressed,
though it's not clear how the final result will compare to python2.

.. _bootstrap_build_options:

Bootstrap
---------

python-for-android supports multiple bootstraps, which contain the app
backend that starts the app and the python interpreter, then
handles interactions with the Android OS.

Currently the following bootstraps are supported, but we hope that it
it should be easy to add others if your project has different
requirements. `Let us know
<https://groups.google.com/forum/#!forum/python-android>`__ if there
are any improvements that would help here.

sdl2
~~~~

Use this with ``--bootstrap=sdl2``, or just include the
``sdl2`` recipe, e.g. ``--requirements=sdl2,python2``.

SDL2 is a popular cross-platform depelopment library, particularly for
games. It has its own Android project support, which
python-for-android uses as a bootstrap, and to which it adds the
Python build and JNI code to start it.

From the point of view of a Python program, SDL2 should behave as
normal. For instance, you can build apps with Kivy or PySDL2
and have them work with this bootstrap. It should also be possible to
use e.g. pygame_sdl2, but this would need a build recipe and doesn't
yet have one.

webview
~~~~~~~

You can use this with ``--bootstrap=webview``, or include the
``webviewjni`` recipe, e.g. ``--requirements=webviewjni,python2``.

The webview bootstrap gui is, per the name, a WebView displaying a
webpage, but this page is hosted on the device via a Python
webserver. For instance, your Python code can start a Flask
application, and your app will display and allow the user to navigate
this website.

.. note:: Your Flask script must start the webserver *without*
          :code:``debug=True``. Debug mode doesn't seem to work on
          Android due to use of a subprocess.

This bootstrap will automatically try to load a website on port 5000
(the default for Flask), or you can specify a different option with
the `--port` command line option. If the webserver is not immediately
present (e.g. during the short Python loading time when first
started), it will instead display a loading screen until the server is
ready.


pygame
~~~~~~

You can use this with ``--bootstrap=pygame``, or simply include the
``pygame`` recipe in your ``--requirements``.

The pygame bootstrap is the original backend used by Kivy, and still
works fine for use with Kivy apps. It may also work for pure pygame
apps, but hasn't been developed with this in mind.

This bootstrap will eventually be deprecated in favour of sdl2, but
not before the sdl2 bootstrap includes all the features that would be
lost.
