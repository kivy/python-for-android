.. _troubleshooting:

Troubleshooting
===============

Debug output
------------

Add the ``--debug`` option to any python-for-android command to see
full debug output including the output of all the external tools used
in the compilation and packaging steps.

If reporting a problem by email or irc, it is usually helpful to
include this full log, via e.g. a `pastebin
<http://paste.ubuntu.com/>`_ or `Github gist
<https://gist.github.com/>`_.

Getting help
------------

python-for-android is managed by the Kivy Organisation, and you can
get help with any problems using the same channels as Kivy itself:

- by email to the `kivy-users Google group
  <https://groups.google.com/forum/#!forum/kivy-users>`_
- by irc in the #kivy room at irc.freenode.net
  
If you find a bug, you can also post an issue on the
`python-for-android Github page
<https://github.com/kivy/python-for-android>`_.

Debugging on Android
--------------------

When a python-for-android APK doesn't work, often the only indication
that you get is that it closes. It is important to be able to find out
what went wrong.

python-for-android redirects Python's stdout and stderr to the Android
logcat stream. You can see this by enabling developer mode on your
Android device, enabling adb on the device, connecting it to your PC
(you should see a notification that USB debugging is connected) and
running ``adb logcat``. If adb is not in your PATH, you can find it at
``/path/to/Android/SDK/platform-tools/adb``, or access it through
python-for-android with the shortcut::

    python-for-android logcat

or::

    python-for-android adb logcat

Running logcat command gives a lot of information about what Android is
doing. You can usually see important lines by using logcat's built in
functionality to see only lines with the ``python`` tag (or just
grepping this).

When your app crashes, you'll see the normal Python traceback here, as
well as the output of any print statements etc. that your app
runs. Use these to diagnose the problem just as normal.
    
The adb command passes its arguments straight to adb itself, so you
can also do other debugging tasks such as ``python-for-android adb
devices`` to get the list of connected devices.

For further information, see the Android docs on `adb
<http://developer.android.com/intl/zh-cn/tools/help/adb.html>`_, and
on `logcat
<http://developer.android.com/intl/zh-cn/tools/help/logcat.html>`_ in
particular.

Unpacking an APK
----------------

It is sometimes useful to unpack a pacakged APK to see what is inside,
especially when debugging python-for-android itself.

APKs are just zip files, so you can extract the contents easily::

  unzip YourApk.apk

At the top level, this will always contain the same set of files::

  $ ls
  AndroidManifest.xml  classes.dex  META-INF     res
  assets               lib          YourApk.apk  resources.arsc

The Python distribution is in the assets folder::

  $ cd assets
  $ ls 
  private.mp3

``private.mp3`` is actually a tarball containing all your packaged
data, and the Python distribution. Extract it::

  $ tar xf private.mp3

This will reveal all the Python-related files::

  $ ls
  android_runnable.pyo  include          interpreter_subprocess  main.kv   pipinterface.kv   settings.pyo
  assets                __init__.pyo     interpreterwrapper.pyo  main.pyo  pipinterface.pyo  utils.pyo
  editor.kv             interpreter.kv   lib                     menu.kv   private.mp3       widgets.pyo
  editor.pyo            interpreter.pyo  libpymodules.so         menu.pyo  settings.kv

Most of these files have been included by the user (in this case, they
come from one of my own apps), the rest relate to the python
distribution.

With Python 2, the Python installation can mostly be found in the
``lib`` folder. With Python 3 (using the ``python3crystax`` recipe),
the Python installation can be found in a folder named
``crystax_python``.


Common errors
-------------

The following are common problems and resolutions that users have reported.


AttributeError: 'AnsiCodes' object has no attribute 'LIGHTBLUE_EX'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This occurs if your version of colorama is too low, install version
0.3.3 or higher.

If you install python-for-android with pip or via setup.py, this
dependency should be taken care of automatically.

AttributeError: 'Context' object has no attribute 'hostpython'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a known bug in some releases. To work around it, add your
python requirement explicitly,
e.g. :code:`--requirements=python2,kivy`. This also applies when using
buildozer, in which case add python2 to your buildozer.spec requirements.

linkname too long
~~~~~~~~~~~~~~~~~

This can happen when you try to include a very long filename, which
doesn't normally happen but can occur accidentally if the p4a
directory contains a .buildozer directory that is not excluded from
the build (e.g. if buildozer was previously used). Removing this
directory should fix the problem, and is desirable anyway since you
don't want it in the APK.

Exception in thread "main" java.lang.UnsupportedClassVersionError: com/android/dx/command/Main : Unsupported major.minor version 52.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This occurs due to a java version mismatch, it should be fixed by
installing Java 8 (e.g. the openjdk-8-jdk package on Ubuntu).

JNI DETECTED ERROR IN APPLICATION: static jfieldID 0x0000000 not valid for class java.lang.Class<org.renpy.android.PythonActivity>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This error appears in the logcat log if you try to access
``org.renpy.android.PythonActivity`` from within the new toolchain. To
fix it, change your code to reference
``org.kivy.android.PythonActivity`` instead.

websocket-client: if you see errors relating to 'SSL not available'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Ensure you have the package backports.ssl-match-hostname in the buildozer requirements, since Kivy targets python 2.7.x
 
You may also need sslopt={"cert_reqs": ssl.CERT_NONE} as a parameter to ws.run_forever() if you get an error relating to host verification

Requested API target 19 is not available, install it with the SDK android tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This means that your SDK is missing the required platform tools. You
need to install the ``platforms;android-19`` package in your SDK,
using the ``android`` or ``sdkmanager`` tools (depending on SDK
version).

If using buildozer this should be done automatically, but as a
workaround you can run these from
``~/.buildozer/android/platform/android-sdk-20/tools/android``.
