Android Python module
=====================

Python for android project include a python module named "android". This module is designed to give you an access to the Android API. As for today, the module is very limited, and waiting for contribution to wrap more Android API.

Example
-------

::

    import android

    # activate the vibrator
    android.vibrate(1)

    # read screen dpi
    print android.get_dpi()

How it's working
----------------

The whole Android API is accessible in Java. Their is no native or extensible way to access it from Python. The schema for accessing to their API is:

    [1] Cython -> [2] C JNI -> [3] Java

#. The ``android.pyx`` is written in Cython: a language with typed informations, very close to Python, that generate Python extension. It's easier to write in Cython than CPython, and it's linked directly to the part 2.
#. The second part define simple c methods that access to Java interfaces through JNI in the file ``android_jni.c``.
#. The last part contain the Java code that will be called from the JNI stuff.

All the source code is available at:

    https://github.com/kivy/python-for-android/tree/master/recipes/android/src


API
---

TODO
