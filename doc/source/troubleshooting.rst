
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

Common errors
-------------

The following are common errors that can arise during the use of
python-for-android, along with solutions where possible.
