python-for-android
==================

python-for-android is an open source build tool to let you package
Python code into standalone android APKs that can be passed around,
installed, or uploaded to marketplaces such as the Play Store
just like any other Androip app. This tool was originally developed
for the Kivy cross-platform graphical framework, but now supports
multiple bootstraps and can be easily extended to package other types
of Python app.

python-for-android supports two major operations; first, it can
compile the Python interpreter, its dependencies, backend libraries
and python code for Android devices. This stage is fully customisable,
you can install as many or few components as you like. Only the
compilation step is carried out, so the result is a standalone Android
project which can be used to generate any number of different APKs,
even with different names, icons, Python code etc.

The second function of python-for-android is to provide a simple
interface to these distributions. You don't have to compile your own,
but can download precompiled versions to package your Python code on
almost any platform including Windows, Linux, and OS X.

See the quickstart etc.

Contents:

.. toctree::
   :maxdepth: 2

To include:

- install guide
- quickstart
- doc for dist build
- doc for dist download
- doc for build.py use
- doc for various commands
- contribute
- examples


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

