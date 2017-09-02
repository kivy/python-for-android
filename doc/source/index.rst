python-for-android
==================

python-for-android is an open source build tool to let you package
Python code into standalone android APKs that can be passed around,
installed, or uploaded to marketplaces such as the Play Store just
like any other Android app. This tool was originally developed for the
`Kivy cross-platform graphical framework <http://kivy.org/#home>`_,
but now supports multiple bootstraps and can be easily extended to
package other types of Python app for Android.

python-for-android supports two major operations; first, it can
compile the Python interpreter, its dependencies, backend libraries
and python code for Android devices. This stage is fully customisable,
you can install as many or few components as you like.  The result is
a standalone Android project which can be used to generate any number
of different APKs, even with different names, icons, Python code etc.
The second function of python-for-android is to provide a simple
interface to these distributions, to generate from such a project a
Python APK with build parameters and Python code to taste.


Contents
========

.. toctree::
   :maxdepth: 2

   quickstart
   buildoptions
   commands
   distutils
   recipes
   bootstraps
   services
   apis
   troubleshooting
   launcher
   contribute
   old_toolchain/index.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
