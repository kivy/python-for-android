
Commands
========

This page documents all the commands and options that can be passed to
toolchain.py.


Commands index
--------------

The commands available are the methods of the ToolchainCL class,
documented below. They may have options of their own, or you can
always pass `general arguments`_ or `distribution arguments`_ to any
command (though if irrelevant they may not have an effect).

.. autoclass:: toolchain.ToolchainCL
   :members:


General arguments
-----------------

These arguments may be passed to any command in order to modify its
behaviour, though not all commands make use of them.

``--debug``
  Print extra debug information about the build, including all compilation output.

``--sdk_dir``
  The filepath where the Android SDK is installed. This can
  alternatively be set in several other ways.

``--android_api``
  The Android API level to target; python-for-android will check if
  the platform tools for this level are installed.

``--ndk_dir``
  The filepath where the Android NDK is installed. This can
  alternatively be set in several other ways.

``--ndk_version``
  The version of the NDK installed, important because the internal
  filepaths to build tools depend on this. This can alternatively be
  set in several other ways, or if your NDK dir contains a RELEASE.TXT
  containing the version this is automatically checked so you don't
  need to manually set it.


Distribution arguments
----------------------

p4a supports several arguments used for specifying which compiled
Android distribution you want to use. You may pass any of these
arguments to any command, and if a distribution is required they will
be used to load, or compile, or download this as necessary.

None of these options are essential, and in principle you need only
supply those that you need.


``--name NAME``
  The name of the distribution. Only one distribution with a given name can be created.

``--requirements LIST,OF,REQUIREMENTS`` 
  The recipes that your
  distribution must contain, as a comma separated list. These must be
  names of recipes or the pypi names of Python modules.

``--force-build BOOL``
  Whether the distribution must be compiled from scratch.

``--arch``
  The architecture to build for. You can specify multiple architectures to build for
  at the same time. As an example ``p4a ... --arch arm64-v8a --arch armeabi-v7a ...``
  will build a distribution for both ``arm64-v8a`` and ``armeabi-v7a``.

``--bootstrap BOOTSTRAP``
  The Java bootstrap to use for your application. You mostly don't
  need to worry about this or set it manually, as an appropriate
  bootstrap will be chosen from your ``--requirements``. Current
  choices are ``sdl2`` (used with Kivy and most other apps), ``webview`` or ``qt``.


.. note:: These options are preliminary. Others will include toggles
          for allowing downloads, and setting additional directories
          from which to load user dists.
