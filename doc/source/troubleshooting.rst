.. _troubleshooting:

Troubleshooting
===============

Debug output
------------

Add the ``--debug`` option to any python-for-android command to see
full debug output including the output of all the external tools used
in the compilation and packaging steps.

If reporting a problem by email or Discord, it is usually helpful to
include this full log, e.g. via a `pastebin
<http://paste.ubuntu.com/>`_ or `Github gist
<https://gist.github.com/>`_.

Getting help
------------

python-for-android is managed by the Kivy Organisation, and you can
get help with any problems using the same channels as Kivy itself:

- by email to the `kivy-users Google group
  <https://groups.google.com/forum/#!forum/kivy-users>`_
- on `#support Discord channel <https://chat.kivy.org/>`_

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

It is sometimes useful to unpack a packaged APK to see what is inside,
especially when debugging python-for-android itself.

APKs are just zip files, so you can extract the contents easily::

  unzip YourApk.apk

At the top level, this will always contain the same set of files::

  $ ls
  AndroidManifest.xml  classes.dex  META-INF     res
  assets               lib          YourApk.apk  resources.arsc

The user app data (code, images, fonts ..) is packaged into a single tarball contained in the assets folder::

  $ cd assets
  $ ls
  private.tar

``private.tar`` is a tarball containing all your packaged
data. Extract it::

  $ tar xf private.tar

This will reveal all the user app data (the files shown below are from the touchtracer demo)::

  $ ls
  README.txt		android.txt		icon.png		main.pyc		p4a_env_vars.txt	particle.png
  private.tar		touchtracer.kv

Due to how We're required to ship ABI-specific things in Android App Bundle,
the Python installation is packaged separately, as (most of it) is ABI-specific.

For example, the Python installation for ``arm64-v8a`` is available in ``lib/arm64-v8a/libpybundle.so``

``libpybundle.so`` is a tarball (but named like a library for packaging requirements), that contains our ``_python_bundle``::

  $ tar xf libpybundle.so
  $ cd _python_bundle
  $ ls
  modules		site-packages	stdlib.zip



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
e.g. :code:`--requirements=python3,kivy`. This also applies when using
buildozer, in which case add python3 to your buildozer.spec requirements.

linkname too long
~~~~~~~~~~~~~~~~~

This can happen when you try to include a very long filename, which
doesn't normally happen but can occur accidentally if the p4a
directory contains a .buildozer directory that is not excluded from
the build (e.g. if buildozer was previously used). Removing this
directory should fix the problem, and is desirable anyway since you
don't want it in the APK.

Requested API target 19 is not available, install it with the SDK android tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This means that your SDK is missing the required platform tools. You
need to install the ``platforms;android-19`` package in your SDK,
using the ``android`` or ``sdkmanager`` tools (depending on SDK
version).

If using buildozer this should be done automatically, but as a
workaround you can run these from
``~/.buildozer/android/platform/android-sdk-20/tools/android``.

ModuleNotFoundError: No module named '_ctypes'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You do not have the libffi headers available to python-for-android, so you need to install them. On Ubuntu and derivatives these come from the `libffi-dev` package.

After installing the headers, clean the build (`p4a clean builds`, or with buildozer delete the `.buildozer` directory within your app directory) and run python-for-android again.

SSLError("Can't connect to HTTPS URL because the SSL module is not available.")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your `hostpython3` was compiled without SSL support. You need to install the SSL development files before rebuilding the `hostpython3` recipe.
Remember to always clean the build before rebuilding (`p4a clean builds`, or with buildozer `buildozer android clean`).

On Ubuntu and derivatives::

    apt install libssl-dev
    p4a clean builds # or with: buildozer `buildozer android clean

On macOS::

    brew install openssl
    sudo ln -sfn /usr/local/opt/openssl /usr/local/ssl
    p4a clean builds # or with: buildozer `buildozer android clean
