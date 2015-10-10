Toolchain
=========

Introduction
------------

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

    For the moment, we are shipping only one "java bootstrap" (needed for
    decompressing your packaged zip file project, create an OpenGL ES 2.0
    surface, handle touch input and manage an audio thread).

    If you want to use it without kivy module (an opengl es 2.0 ui toolkit),
    then you might want a lighter java bootstrap, that we don't have right now.
    Help is welcome :)
    
    So for the moment, Python for Android can only be used with the kivy GUI toolkit:
    http://kivy.org/#home


How does it work ?
------------------

To be able to run Python on android, you need to compile it for android. And
you need to compile all the libraries you want for android too.
Since Python is a language, not a toolkit, you cannot draw any user interface
with it: you need to use a toolkit for it. Kivy can be one of them.

So for a simple ui project, the first step is to compile Python + Kivy + all
others libraries. Then you'll have what we call a "distribution".
A distribution is composed of:

- Python
- Python libraries
- All selected libraries (kivy, pygame, pil...)
- A java bootstrap
- A build script

You'll use the build script for create an "apk": an android package.


.. include:: prerequisites.rst
.. include:: usage.rst
.. include:: customize.rst

.. toctree::
    :hidden:

    prerequisites
    usage
    customize
