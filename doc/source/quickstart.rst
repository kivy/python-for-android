
Quickstart
==========

These simple steps run through the most simple procedure to create an
APK with some simple default parameters. See the :doc:`commands
documentation <commands>` for all the different commands and build
options available.

.. warning:: These instructions are quite preliminary. The
             installation and use process will become more standard in
             the near future.


Installation
------------

The easiest way to install is with pip. You need to have setuptools installed, then run::

  pip install git+https://github.com/kivy/python-for-android.git

This should install python-for-android (though you may need to run as root or add --user).

You could also install python-for-android manually, either via git::

  git clone https://github.com/kivy/python-for-android.git
  cd python-for-android

Or by direct download::

  wget https://github.com/kivy/python-for-android/archive/master.zip
  unzip revamp.zip
  cd python-for-android-revamp

Then in both cases run ``python setup.py install``.

Dependencies
------------

python-for-android has several dependencies that must be installed,
via your package manager or otherwise. These include:

- git
- ant
- python2
- cython (can be installed via pip)
- the Android `SDK <https://developer.android.com/sdk/index.html#Other>`_ and `NDK <https://developer.android.com/ndk/downloads/index.html>`_ (see below)
- a Java JDK (e.g. openjdk-7)
- zlib (including 32 bit)
- libncurses (including 32 bit)
- unzip
- virtualenv (can be installed via pip)
- ccache (optional)

On recent versions of Ubuntu and its derivatives you may be able to
install most of these with::

    sudo dpkg --add-architecture i386
    sudo apt-get update
    sudo apt-get install -y build-essential ccache git zlib1g-dev python2.7 python2.7-dev libncurses5:i386 libstdc++6:i386 zlib1g:i386 openjdk-7-jdk unzip ant

When installing the Android SDK and NDK, note the filepaths where they
may be found, and the version of the NDK installed. You may need to
set environment variables pointing to these later.

.. _basic_use:

Basic use
---------

python-for-android provides two executables, ``python-for-android``
and ``p4a``. These are identical and interchangeable, you can
substitute either one for the other. These instructions all use
``python-for-android``.

You can test that p4a was installed correctly by running
``python-for-android recipes``. This should print a list of all the
recipes available to be built into your APKs.

Before running any apk packaging or distribution creation, it is
essential to set some env vars. Make sure you have installed the
Android SDK and NDK, then:

- Set the ``ANDROIDSDK`` env var to the ``/path/to/the/sdk``
- Set the ``ANDROIDNDK`` env var to the ``/path/to/the/ndk``
- Set the ``ANDROIDAPI`` to the targeted API version (or leave it
  unset to use the default of ``14``).
- Set the ``ANDROIDNDKVER`` env var to the version of the NDK
  downloaded, e.g. the current NDK is ``r10e`` (or leave it unset to
  use the default of ``r9``.

This is **NOT** the only way to set these variables, see the `setting
SDK/NDK paths <setting_paths_>`_ section for other options and their
details.

To create a basic distribution, run .e.g::

     python-for-android create --dist_name=testproject --bootstrap=pygame \
         --requirements=sdl,python2

This will compile the distribution, which will take a few minutes, but
will keep you informed about its progress. The arguments relate to the
properties of the created distribution; the dist_name is an (optional)
unique identifier, and the requirements is a list of any pure Python
pypi modules, or dependencies with recipes available, that your app
depends on. The full list of builtin internal recipes can be seen with
``python-for-android recipes``.

.. note:: Compiled dists are not located in the same place as with old
          python-for-android, but instead in an OS-dependent
          location. The build process will print this location when it
          finishes, but you no longer need to navigate there manually
          (see below).

To build an APK, use the ``apk`` command::

    python-for-android apk --private /path/to/your/app --package=org.example.packagename \
        --name="Your app name" --version=0.1

The arguments to ``apk`` can be anything accepted by the old
python-for-android build.py; the above is a minimal set to create a
basic app. You can see the list with ``python-for-android apk help``.

A new feature of python-for-android is that you can do all of this with just one command::

    python-for-android apk --private /path/to/your/app \
        --package=org.example.packagename --name="Your app name" --version=0.5
        --bootstrap=pygame --requirements=sdl,python2 --dist_name=testproject

This combines the previous ``apk`` command with the arguments to
``create``, and works in exactly the same way; if no internal
distribution exists with these requirements then one is first built,
before being used to package the APK. When the command is run again,
the build step is skipped and the previous dist re-used.

Using this method you don't have to worry about whether a dist exists,
though it is recommended to use a different ``dist_name`` for each
project unless they have precisely the same requirements.

You can build an SDL2 APK similarly, creating a dist as follows::

    python-for-android create --dist_name=testsdl2 --bootstrap=sdl2 --requirements=sdl2,python2

You can then make an APK in the same way, but this is more
experimental and doesn't support as much customisation yet.

Your APKs are not limited to Kivy, for instance you can create apps
using Vispy, or using PySDL2 directly. The basic command for this
would be e.g.::

    python-for-android create --dist_name=testvispy --bootstrap=sdl2 --requirements=vispy

python-for-android also has commands to list internal information
about distributions available, to export or symlink these (they come
with a standalone APK build script), and in future will also support
features including binary download to avoid the manual compilation
step.

See the :doc:`commands` documentation for full details of available
functionality.

.. _setting_paths:

Setting paths to the the SDK and NDK
------------------------------------

If building your own dists it is necessary to have installed the
Android SDK and NDK, and to make Kivy aware of their locations. The
instructions in `basic use <basic_use_>`_ use environment variables
for this, but this is not the only option. The different possibilities
for each setting are given below.

Path to the Android SDK
~~~~~~~~~~~~~~~~~~~~~~~

python-for-android searches in the following places for this path, in
order; setting any of these variables overrides all the later ones:

- The ``--sdk_dir`` argument to any python-for-android command.
- The ``ANDROIDSDK`` environment variable.
- The ``ANDROID_HOME`` environment variable (this may be used or set
  by other tools).
- By using buildozer and letting it download the SDK;
  python-for-android automatically checks the default buildozer
  download directory. This is intended to make testing
  python-for-android easy.

If none of these is set, python-for-android will raise an error and exit.

The Android API to target
~~~~~~~~~~~~~~~~~~~~~~~~~

When building for Android it is necessary to target an API number
corresponding to a specific version of Android. Whatever you choose,
your APK will probably not work in earlier versions, but you also
cannot use features introduced in later versions.

You must download specific platform tools for the SDK for any given
target, it does not come with any. Do this by running
``/path/to/android/sdk/tools/android``, which will give a gui
interface, and select the 'platform tools' option under your chosen
target.

The default target of python-for-android is 14, corresponding to
Android 4.0. This may be changed in the near future.

You must pass the target API to python-for-android, and can do this in
several ways. Each choice overrides all the later ones:

- The ``--android_api`` argument to any python-for-android command.
- The ``ANDROIDAPI`` environment variables.
- If neither of the above, the default target is used (currently 14).

python-for-android checks if the target you select is available, and
gives an error if not, so it's easy to test if you passed this
variable correctly.

Path to the Android NDK
~~~~~~~~~~~~~~~~~~~~~~~

python-for-android searches in the following places for this path, in
order; setting any of these variables overrides all the later ones:

- The ``--ndk_dir`` argument to any python-for-android command.
- The ``ANDROIDNDK`` environment variable.
- The ``NDK_HOME`` environment variable (this may be used or set
  by other tools).
- The ``ANDROID_NDK_HOME`` environment variable (this may be used or set
- By using buildozer and letting it download the NDK;
  python-for-android automatically checks the default buildozer
  download directory. This is intended to make testing
  python-for-android easy.
  by other tools).

If none of these is set, python-for-android will raise an error and exit.

The Android NDK version
~~~~~~~~~~~~~~~~~~~~~~~

python-for-android needs to know what version of the NDK is installed,
in order to properly resolve its internal filepaths. You can set this
with any of the following methods - note that the first is preferred,
and means that you probably do *not* have to manually set this.

- The ``RELEASE.TXT`` file in the NDK directory. If this exists and
  contains the version (which it probably does automatically), you do
  not need to set it manually.
- The ``--ndk_ver`` argument to any python-for-android command.
- The ``ANDROIDNDKVER`` environment variable.

If ``RELEASE.TXT`` exists but you manually set a different version,
python-for-android will warn you about it, but will assume you are
correct and try to continue the build.

Configuration file
~~~~~~~~~~~~~~~~~~

python-for-android checks in the current directory for a configuration
file named ``.p4a``. If found, it adds all the lines as options to the
command line. For example, you can add the options you would always
include such as:

    --dist_name my_example
    --android_api 19
    --requirements kivy,openssl
