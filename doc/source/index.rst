python-for-android
==================

python-for-android (p4a) is a development tool that packages Python apps into
binaries that can run on Android devices.

It can generate Android Package (APK) files, which can be installed on Android
with everything it needs to run. It can generate both debug and signed release
APKs - the latter can be shared on marketplaces, like
`Google Play Store <https://play.google.com/store/>`_.

It can also generate
`Android App Bundle <https://developer.android.com/guide/app-bundle/faq>`_ (AAB)
files that can be bundled with others into an APK.

It supports multiple CPU architectures.

It supports apps developed with `Kivy framework <http://kivy.org>`_, but was
built to be flexible about the backend libraries (through "bootstraps"), and
also supports `PySDL2 <https://pypi.org/project/PySDL2/>`_, and a
`WebView <https://developer.android.com/reference/android/webkit/WebView>`_ with
a Python web server.

It automatically supports dependencies on most pure Python packages. For other
packages, including those that depend on C code, a special "recipe" must be
written to support cross-compiling. python-for-android comes with recipes for
many of the mosty popular libraries (e.g. numpy and sqlalchemy) built in.

python-for-android works by cross-compiling the Python interpreter and its
dependencies for Android devices, and bundling it with the app's python code
and dependencies. The Python code is then interpreted on the Android device.

It is recommended that python-for-android be used via
`Buildozer <https://buildozer.readthedocs.io/>`_, which ensures the correct
dependencies are pre-installed, and centralizes the configuration. However,
python-for-android is not limited to being used with Buildozer.

Buildozer is released and distributed under the terms of the MIT license. You
should have received a
copy of the MIT license alongside your distribution. Our
`latest license <https://github.com/kivy/python-for-android/blob/master/LICENSE>`_
is also available.


Contents
========

.. toctree::
   :maxdepth: 2

   quickstart
   buildoptions
   commands
   apis
   distutils
   recipes
   bootstraps
   services
   troubleshooting
   docker
   testing_pull_requests
   faq
   contribute
   contact


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
