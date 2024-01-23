
Build options
=============

This page contains instructions for using different build options.


Python versions
---------------

python-for-android supports using Python 3.8 or higher. To explicitly select a Python
version in your requirements, use e.g. ``--requirements=python3==3.10.11,hostpython3==3.10.11``.

The last python-for-android version supporting Python2 was `v2019.10.06 <https://github.com/kivy/python-for-android/archive/v2019.10.06.zip>`__

Python-for-android no longer supports building for Python 3 using the CrystaX
NDK. The last python-for-android version supporting CrystaX was `0.7.0 <https://github.com/kivy/python-for-android/archive/0.7.0.zip>`__

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
``sdl2`` recipe, e.g. ``--requirements=sdl2,python3``.

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
- ``--orientation``: The orientations that the app will display in.
  (Available options are ``portrait``, ``landscape``, ``portrait-reverse``, ``landscape-reverse``).
  Since Android ignores ``android:screenOrientation`` when in multi-window mode
  (Which is the default on Android 12+), this option will also set the window orientation hints
  for the SDL bootstrap. If multiple orientations are given,
  ``android:screenOrientation`` will be set to ``unspecified``.
- ``--manifest-orientation``: The orientation that will be set for the ``android:screenOrientation``
  attribute of the activity in the ``AndroidManifest.xml`` file. If not set, the value 
  will be synthesized from the ``--orientation`` option.
  The full list of valid options is given under ``android:screenOrientation``
  in the `Android documentation <https://developer.android.com/guide/topics/manifest/activity-element.html>`__.
- ``--icon``: A path to the png file to use as the application icon.
- ``--permission``: A permission that needs to be declared into the App ``AndroidManifest.xml``.
  For multiple permissions, add multiple ``--permission`` arguments.
  ``--home-app`` Gives you the option to set your application as a home app (launcher) on your Android device.

  .. Note ::
    ``--permission`` accepts the following syntaxes: 
    ``--permission (name=android.permission.WRITE_EXTERNAL_STORAGE;maxSdkVersion=18)``
    or ``--permission android.permission.WRITE_EXTERNAL_STORAGE``.

    The first syntax is used to set additional properties to the permission 
    (``android:maxSdkVersion`` and ``android:usesPermissionFlags`` are the only ones supported for now).

    The second one can be used when there's no need to add any additional properties.

  .. Warning ::
    The syntax ``--permission VIBRATE`` (only the permission name, without the prefix),
    is also supported for backward compatibility, but it will be removed in the future.


- ``--meta-data``: Custom key=value pairs to add in the application metadata.
- ``--presplash``: A path to the image file to use as a screen while
  the application is loading.
- ``--presplash-color``: The presplash screen background color, of the
  form ``#RRGGBB`` or a color name ``red``, ``green``, ``blue`` etc.
- ``--presplash-lottie``: use a lottie (json) file as a presplash animation. If
  used, this will replace the static presplash image.
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
- ``--no-byte-compile-python``: Skip byte compile for .py files.
- ``--enable-androidx``: Enable AndroidX support library.
- ``--add-resource``: Put this file or directory in the apk res directory.


webview
~~~~~~~

You can use this with ``--bootstrap=webview``, or include the
``webviewjni`` recipe, e.g. ``--requirements=webviewjni,python3``.

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
- ``--orientation``: The orientations that the app will display in.
  (Available options are ``portrait``, ``landscape``, ``portrait-reverse``, ``landscape-reverse``).
  Since Android ignores ``android:screenOrientation`` when in multi-window mode
  (Which is the default on Android 12+), this setting is not guaranteed to work, and
  you should consider to implement a custom orientation change handler in your app.
- ``--manifest-orientation``: The orientation that will be set in the ``android:screenOrientation``
  attribute of the activity in the ``AndroidManifest.xml`` file. If not set, the value 
  will be synthesized from the ``--orientation`` option.
  The full list of valid options is given under ``android:screenOrientation``
  in the `Android documentation <https://developer.android.com/guide/topics/manifest/activity-element.html>`__.
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
- ``add-source``: Add a source directory to the app's Java code.
- ``--port``: The port on localhost that the WebView will
  access. Defaults to 5000.


service_library
~~~~~~~~~~~~~~~

You can use this with ``--bootstrap=service_library`` option.


This bootstrap can be used together with ``aar`` output target to generate
a library, containing Python services that can be used with other build 
systems and frameworks.

- ``--private``: The directory containing your project files.
- ``--package``: The Java package name for your project. e.g. ``org.example.yourapp``.
- ``--name``: The library name.
- ``--version``: The version number.
- ``--service``: A service name and the Python script it should
  run. See :ref:`arbitrary_scripts_services`.
- ``--blacklist``: The path to a file containing blacklisted patterns
  that will be excluded from the final AAR. Defaults to ``./blacklist.txt``.
- ``--whitelist``: The path to a file containing whitelisted patterns
  that will be included in the AAR even if also blacklisted.
- ``--add-jar``: The path to a .jar file to include in the APK. To
  include multiple jar files, pass this argument multiple times.
- ``add-source``: Add a source directory to the app's Java code.

Qt
~~

This bootstrap can be used with ``--bootstrap=qt`` or by including the ``PySide6`` or
``shiboken6`` recipe, e.g. ``--requirements=pyside6,shiboken6``. Currently, the only way
to use this bootstrap is through `pyside6-android-deploy <https://www.qt.io/blog/taking-qt-for-python-to-android>`__
tool shipped with ``PySide6``, as the recipes for ``PySide6`` and ``shiboken6`` are created
dynamically. The tool builds ``PySide6`` and ``shiboken6`` wheels for a specific Android platform
and the recipes simply unpack the built wheels. You can see the recipes `here <https://code.qt.io/cgit/pyside/pyside-setup.git/tree/sources/pyside-tools/deploy_lib/android/recipes>`__.

.. note::
  The ``pyside6-android-deploy`` tool and hence the Qt bootstrap does not support multi-architecture
  builds currently.

What are Qt and PySide?
%%%%%%%%%%%%%%%%%%%%%%%%

`Qt <https://www.qt.io/>`__ is a popularly used cross-platform C++ framework for developing
GUI applications. `PySide6 <https://doc.qt.io/qtforpython-6/quickstart.html>`__ refers to the
Python bindings for Qt6, and enables the Python developers access to the Qt6 API.
`Shiboken6 <https://doc.qt.io/qtforpython-6/shiboken6/index.html>`__ is the binding generator
tool used for generating the Python bindings from C++ code.

.. note:: The `shiboken6` recipe is for the `Shiboken Python module <https://doc.qt.io/qtforpython-6/shiboken6/shibokenmodule.html>`__
  which includes a couple of utility functions for inspecting and debugging PySide6 code.

Build Options
%%%%%%%%%%%%%

``pyside6-android-deploy`` works by generating a ``buildozer.spec`` file and thereby using
`buildozer <https://buildozer.readthedocs.io/en/latest/>`__ to control the build options used by
``python-for-android`` with the Qt bootstrap. Apart from the general build options that works
across all the other bootstraps, the Qt bootstrap introduces the following 3 new build options.

- ``--qt-libs``: list of Qt libraries(modules) to be loaded.
- ``--load-local-libs``: list of Qt plugin libraries to be loaded.
- ``--init-classes``: list of Java class names to the loaded from the Qt jar files supplied through
  the ``--add-jar`` option.

These build options are automatically populated by the ``pyside6-android-deploy`` tool, but can be
modified by updating the ``buildozer.spec`` file. Apart from the above 3 build options, the tool
also automatically identifies the values to be fed into the cli options ``--permission``, ``--add-jar``
depending on the PySide6 modules used by the applicaiton.

Requirements blacklist (APK size optimization)
----------------------------------------------

To optimize the size of the `.apk` file that p4a builds for you,
you can **blacklist** certain core components. Per default, p4a
will add python *with batteries included* as would be expected on
desktop, including openssl, sqlite3 and other components you may
not use.

To blacklist an item, specify the ``--blacklist-requirements`` option::

    p4a apk ... --blacklist-requirements=sqlite3

At the moment, the following core components can be blacklisted
(if you don't want to use them) to decrease APK size:

- ``android``  disables p4a's android module (see :ref:`reference-label-for-android-module`)
- ``libffi``  disables ctypes stdlib module
- ``openssl``   disables ssl stdlib module
- ``sqlite3``   disables sqlite3 stdlib module
