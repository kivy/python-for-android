
Build options
=============

This page contains instructions for using different build options.


Python versions
---------------

python2
~~~~~~~

Select this by adding it in your requirements, e.g. ``--requirements=python2``.

This option builds Python 2.7.2 for your selected Android
architecture. There are no special requirements, all the building is
done locally.


python3
~~~~~~~

Python3 is supported in two ways. The default method uses CPython 3.7+
and works with any recent version of the Android NDK.

Select Python 3 by adding it to your requirements,
e.g. ``--requirements=python3``.


CrystaX python3
###############

.. warning:: python-for-android originally supported Python 3 using the CrystaX
             NDK. This support is now being phased out as CrystaX is no longer
             actively developed.

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

.. _bootstrap_build_options:

Bootstrap options
-----------------

python-for-android supports multiple app backends with different types
of interface. These are called *bootstraps*.

Currently the following bootstraps are supported, but we hope that it
should be easy to add others if your project has different
requirements. `Let us know
<https://groups.google.com/forum/#!forum/python-android>`__ if you'd
like help adding a new one.

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

Build options
%%%%%%%%%%%%%

The sdl2 bootstrap supports the following additional command line
options (this list may not be exhaustive):

- ``--private``: The directory containing your project files.
- ``--package``: The Java package name for your project. e.g. ``org.example.yourapp``.
- ``--name``: The app name.
- ``--version``: The version number.
- ``--orientation``: Usually one of ``portait``, ``landscape``,
  ``sensor`` to automatically rotate according to the device
  orientation, or ``user`` to do the same but obeying the user's
  settings. The full list of valid options is given under
  ``android:screenOrientation`` in the `Android documentation
  <https://developer.android.com/guide/topics/manifest/activity-element.html>`__.
- ``--icon``: A path to the png file to use as the application icon.
- ``--permission``: A permission name for the app,
  e.g. ``--permission VIBRATE``. For multiple permissions, add
  multiple ``--permission`` arguments.
- ``--meta-data``: Custom key=value pairs to add in the application metadata.
- ``--presplash``: A path to the image file to use as a screen while
  the application is loading.
- ``--presplash-color``: The presplash screen background color, of the
  form ``#RRGGBB`` or a color name ``red``, ``green``, ``blue`` etc.
- ``--wakelock``: If the argument is included, the application will
  prevent the device from sleeping.
- ``--window``: If the argument is included, the application will not
  cover the Android status bar.
- ``--blacklist``: The path to a file containing blacklisted patterns
  that will be excluded from the final APK. Defaults to ``./blacklist.txt``.
- ``--whitelist``: The path to a file containing whitelisted patterns
  that will be included in the APK even if also blacklisted.
- ``--add-jar``: The path to a .jar file to include in the APK. To
  include multiple jar files, pass this argument multiple times.
- ``--intent-filters``: A file path containing intent filter xml to be
  included in AndroidManifest.xml.
- ``--service``: A service name and the Python script it should
  run. See :ref:`arbitrary_scripts_services`.
- ``--add-source``: Add a source directory to the app's Java code.
- ``--no-compile-pyo``: Do not optimise .py files to .pyo.


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

- ``--private``: The directory containing your project files.
- ``--package``: The Java package name for your project. e.g. ``org.example.yourapp``.
- ``--name``: The app name.
- ``--version``: The version number.
- ``--orientation``: Usually one of ``portait``, ``landscape``,
  ``sensor`` to automatically rotate according to the device
  orientation, or ``user`` to do the same but obeying the user's
  settings. The full list of valid options is given under
  ``android:screenOrientation`` in the `Android documentation
  <https://developer.android.com/guide/topics/manifest/activity-element.html>`__.
- ``--icon``: A path to the png file to use as the application icon.
- ``-- permission``: A permission name for the app,
  e.g. ``--permission VIBRATE``. For multiple permissions, add
  multiple ``--permission`` arguments.
- ``--meta-data``: Custom key=value pairs to add in the application metadata.
- ``--presplash``: A path to the image file to use as a screen while
  the application is loading.
- ``--presplash-color``: The presplash screen background color, of the
  form ``#RRGGBB`` or a color name ``red``, ``green``, ``blue`` etc.
- ``--wakelock``: If the argument is included, the application will
  prevent the device from sleeping.
- ``--window``: If the argument is included, the application will not
  cover the Android status bar.
- ``--blacklist``: The path to a file containing blacklisted patterns
  that will be excluded from the final APK. Defaults to ``./blacklist.txt``.
- ``--whitelist``: The path to a file containing whitelisted patterns
  that will be included in the APK even if also blacklisted.
- ``--add-jar``: The path to a .jar file to include in the APK. To
  include multiple jar files, pass this argument multiple times.
- ``--intent-filters``: A file path containing intent filter xml to be
  included in AndroidManifest.xml.
- ``--service``: A service name and the Python script it should
  run. See :ref:`arbitrary_scripts_services`.
- ``add-source``: Add a source directory to the app's Java code.
- ``--port``: The port on localhost that the WebView will
  access. Defaults to 5000.


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

Build options
%%%%%%%%%%%%%

The pygame bootstrap supports the following additional command line
options (this list may not be exhaustive):

- ``--private``: The directory containing your project files.
- ``--dir``: The directory containing your project files if you want
  them to be unpacked to the external storage directory rather than
  the app private directory.
- ``--package``: The Java package name for your project. e.g. ``org.example.yourapp``.
- ``--name``: The app name.
- ``--version``: The version number.
- ``--orientation``: One of ``portait``, ``landscape`` or ``sensor``
  to automatically rotate according to the device orientation.
- ``--icon``: A path to the png file to use as the application icon.
- ``--ignore-path``: A path to ignore when including the app
  files. Pass multiple times to ignore multiple paths.
- ``-- permission``: A permission name for the app,
  e.g. ``--permission VIBRATE``. For multiple permissions, add
  multiple ``--permission`` arguments.
- ``--meta-data``: Custom key=value pairs to add in the application metadata.
- ``--presplash``: A path to the image file to use as a screen while
  the application is loading.
- ``--wakelock``: If the argument is included, the application will
  prevent the device from sleeping.
- ``--window``: If the argument is included, the application will not
  cover the Android status bar.
- ``--blacklist``: The path to a file containing blacklisted patterns
  that will be excluded from the final APK. Defaults to ``./blacklist.txt``.
- ``--whitelist``: The path to a file containing whitelisted patterns
  that will be included in the APK even if also blacklisted.
- ``--add-jar``: The path to a .jar file to include in the APK. To
  include multiple jar files, pass this argument multiple times.
- ``--intent-filters``: A file path containing intent filter xml to be
  included in AndroidManifest.xml.
- ``--service``: A service name and the Python script it should
  run. See :ref:`arbitrary_scripts_services`.
- ``add-source``: Add a source directory to the app's Java code.
- ``--compile-pyo``: Optimise .py files to .pyo.
- ``--resource``: A key=value pair to add in the string.xml resource file.
