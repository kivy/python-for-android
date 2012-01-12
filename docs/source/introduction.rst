Introduction
============

In terms of comparaison, you can check how Python for android can be useful
compared to other projects.

+--------------------+---------------+---------------+----------------+--------------+
| Project            | Native Python | GUI libraries | APK generation | Custom build |
+====================+===============+===============+================+==============+
| Python for android | Yes           | Yes           | Yes            | Yes          |
+--------------------+---------------+---------------+----------------+--------------+
| PGS4A              | Yes           | Yes           | Yes            | No           |
+--------------------+---------------+---------------+----------------+--------------+
| Android scripting  | No            | No            | No             | No           |
+--------------------+---------------+---------------+----------------+--------------+
| Python on a chip   | No            | No            | No             | No           |
+--------------------+---------------+---------------+----------------+--------------+

.. note::

    For the moment, we are shipping only one "java bootstrap" needed for
    decompressing all the files of your project, create an OpenGL ES 2.0
    surface, handle touch input and manage an audio thread.

    If you want to use it without kivy module (an opengl es 2.0 ui toolkit),
    then you might want a lighter java bootstrap, that we don't have right now.
    Help is welcome :)


