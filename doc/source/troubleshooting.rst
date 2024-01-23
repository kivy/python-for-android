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
<https://pastebin.ubuntu.com/>`_ or `Github gist
<https://gist.github.com/>`_.

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
<https://developer.android.com/tools/adb>`_, and
on `logcat
<https://developer.android.com/tools/logcat>`_ in
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

FAQ
---

Check out the `online FAQ <https://github.com/kivy/python-for-android/blob/master/FAQ.md>`_ for common
errors.