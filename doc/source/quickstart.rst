
Getting Started
===============

Getting up and running on python-for-android (p4a) is a simple process
and should only take you a couple of minutes. We'll refer to Python
for android as p4a in this documentation.

Concepts
--------

*Basic:*

- **requirements:** For p4a, all your app's dependencies must be specified
  via ``--requirements`` similar to the standard `requirements.txt`.
  (Unless you specify them via a `setup.py`/`install_requires`)
  All dependencies will be mapped to "recipes" if any exist, so that
  many common libraries will just work. See "recipe" below for details.

- **distribution:** A distribution is the final "build" of your
  compiled project + requirements, as an Android project assembled by
  p4a that can be turned directly into an APK. p4a can contain multiple
  distributions with different sets of requirements.

- **build:** A build refers to a compiled recipe or distribution.

- **bootstrap:** A bootstrap is the app backend that will start your
  application. The default for graphical applications is SDL2.
  You can also use e.g. the webview for web apps, or service_only/service_library for
  background services, or qt for PySide6 apps. Different bootstraps have different additional
  build options.

*Advanced:*

- **recipe:**
  A recipe is a file telling p4a how to install a requirement
  that isn't by default fully Android compatible.
  This is often necessary for Cython or C/C++-using python extensions.
  p4a has recipes for many common libraries already included, and any
  dependency you specified will be automatically mapped to its recipe.
  If a dependency doesn't work and has no recipe included in p4a,
  then it may need one to work.


Installation
------------

Installing p4a
~~~~~~~~~~~~~~

p4a is now available on Pypi, so you can install it using pip::

    pip install python-for-android

You can also test the master branch from Github using::

    pip install git+https://github.com/kivy/python-for-android.git

Installing Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~

p4a requires a few dependencies to be installed on your system to work
properly. While we're working on a way to automate pre-requisites checks,
suggestions and installation on all platforms (macOS is already supported),
on Linux distros you'll need to install them manually.

On recent versions of Ubuntu and its derivatives you can easily install them via
the following command (re-adapted from the `Dockerfile` we use to perform CI builds)::

    sudo apt-get update
    sudo apt-get install -y \
        ant \
        autoconf \
        automake \
        ccache \
        cmake \
        g++ \
        gcc \
        git \
        lbzip2 \
        libffi-dev \
        libltdl-dev \
        libtool \
        libssl-dev \
        make \
        openjdk-17-jdk \
        patch \
        pkg-config \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        sudo \
        unzip \
        wget \
        zip


Installing Android SDK
~~~~~~~~~~~~~~~~~~~~~~

.. warning::
   python-for-android is often picky about the **SDK/NDK versions.**
   Pick the recommended ones from below to avoid problems.

Basic SDK install
`````````````````

You need to download and unpack the Android SDK and NDK to a directory (let's say $HOME/Documents/):

- `Android SDK <https://developer.android.com/studio/index.html>`_
- `Android NDK <https://developer.android.com/ndk/downloads/index.html>`_

For the Android SDK, you can download 'just the command line
tools'. When you have extracted these you'll see only a directory
named ``tools``, and you will need to run extra commands to install
the SDK packages needed. 

For Android NDK, note that modern releases will only work on a 64-bit
operating system. **The minimal, and recommended, NDK version to use is r25b:**

 - `Go to ndk downloads page <https://developer.android.com/ndk/downloads/>`_
 - Windows users should create a virtual machine with an GNU Linux os
   installed, and then you can follow the described instructions from within
   your virtual machine.


Platform and build tools
````````````````````````

First, install an API platform to target. **The recommended *target* API
level is 27**, you can replace it with a different number but
keep in mind other API versions are less well-tested and older devices
are still supported down to the **recommended specified *minimum*
API/NDK API level 21**::

  $SDK_DIR/tools/bin/sdkmanager "platforms;android-27"


Second, install the build-tools. You can use
``$SDK_DIR/tools/bin/sdkmanager --list`` to see all the
possibilities, but 28.0.2 is the latest version at the time of writing::

  $SDK_DIR/tools/bin/sdkmanager "build-tools;28.0.2"

Configure p4a to use your SDK/NDK
`````````````````````````````````

Then, you can edit your ``~/.bashrc`` or other favorite shell to include new environment
variables necessary for building on android::

    # Adjust the paths!
    export ANDROIDSDK="$HOME/Documents/android-sdk-27"
    export ANDROIDNDK="$HOME/Documents/android-ndk-r23b"
    export ANDROIDAPI="27"  # Target API version of your application
    export NDKAPI="21"  # Minimum supported API version of your application
    export ANDROIDNDKVER="r10e"  # Version of the NDK you installed

You have the possibility to configure on any command the PATH to the SDK, NDK and Android API using:

- :code:`--sdk-dir PATH` as an equivalent of `$ANDROIDSDK`
- :code:`--ndk-dir PATH` as an equivalent of `$ANDROIDNDK`
- :code:`--android-api VERSION` as an equivalent of `$ANDROIDAPI`
- :code:`--ndk-api VERSION` as an equivalent of `$NDKAPI`
- :code:`--ndk-version VERSION` as an equivalent of `$ANDROIDNDKVER`


Usage
-----

Build a Kivy or SDL2 application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build your application, you need to specify name, version, a package
identifier, the bootstrap you want to use (`sdl2` for kivy or sdl2 apps)
and the requirements::

    p4a apk --private $HOME/code/myapp --package=org.example.myapp --name "My application" --version 0.1 --bootstrap=sdl2 --requirements=python3,kivy

**Note on** ``--requirements``: **you must add all
libraries/dependencies your app needs to run.**
Example: ``--requirements=python3,kivy,vispy``. For an SDL2 app,
`kivy` is not needed, but you need to add any wrappers you might
use (e.g. `pysdl2`).

This `p4a apk ...` command builds a distribution with `python3`,
`kivy`, and everything else you specified in the requirements.
It will be packaged using a SDL2 bootstrap, and produce
an `.apk` file.

*Compatibility notes:*

- Python 2 is no longer supported by python-for-android. The last release supporting Python 2 was v2019.10.06.


Build a WebView application
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build your application, you need to have a name, version, a package
identifier, and explicitly use the webview bootstrap, as
well as the requirements::

    p4a apk --private $HOME/code/myapp --package=org.example.myapp --name "My WebView Application" --version 0.1 --bootstrap=webview --requirements=flask --port=5000

**Please note as with kivy/SDL2, you need to specify all your
additional requirements/dependencies.**

You can also replace flask with another web framework.

Replace ``--port=5000`` with the port on which your app will serve a
website. The default for Flask is 5000.


Build a Service library archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build an android archive (.aar), containing an android service , you need a name, version, package identifier, explicitly use the 
service_library bootstrap, and declare service entry point (See :ref:`services <arbitrary_scripts_services>` for more options), as well as the requirements and arch(s)::

    p4a aar --private $HOME/code/myapp --package=org.example.myapp --name "My library" --version 0.1 --bootstrap=service_library --requirements=python3 --release --service=myservice:service.py --arch=arm64-v8a --arch=armeabi-v7a


You can then call the generated Java entrypoint(s) for your Python service(s) in other apk build frameworks.


Exporting the Android App Bundle (aab) for distributing it on Google Play
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from August 2021 for new apps and from November 2021 for updates to existings apps,
Google Play Console will require the Android App Bundle instead of the long lived apk.

python-for-android handles by itself the needed work to accomplish the new requirements::

    p4a aab --private $HOME/code/myapp --package=org.example.myapp --name="My App" --version 0.1 --bootstrap=sdl2 --requirements=python3,kivy --arch=arm64-v8a --arch=armeabi-v7a --release

This `p4a aab ...` command builds a distribution with `python3`,
`kivy`, and everything else you specified in the requirements.
It will be packaged using a SDL2 bootstrap, and produce
an `.aab` file that contains binaries for both `armeabi-v7a` and `arm64-v8a` ABIs.

The Android App Bundle, is supposed to be used for distributing your app.
If you need to test it locally, on your device, you can use `bundletool <https://developer.android.com/studio/command-line/bundletool>`

Other options
~~~~~~~~~~~~~

You can pass other command line arguments to control app behaviours
such as orientation, wakelock and app permissions. See
:ref:`bootstrap_build_options`.



Rebuild everything
~~~~~~~~~~~~~~~~~~

If anything goes wrong and you want to clean the downloads and builds to retry everything, run::

    p4a clean_all

If you just want to clean the builds to avoid redownloading dependencies, run::

    p4a clean_builds && p4a clean_dists

Getting help
~~~~~~~~~~~~

If something goes wrong and you don't know how to fix it, add the
``--debug`` option and post the output log to the `kivy-users Google
group <https://groups.google.com/forum/#!forum/kivy-users>`__ or the
kivy `#support Discord channel <https://chat.kivy.org/>`_.

See :doc:`troubleshooting` for more information.


Advanced usage
--------------

Recipe management
~~~~~~~~~~~~~~~~~

You can see the list of the available recipes with::

    p4a recipes

If you are contributing to p4a and want to test a recipes again,
you need to clean the build and rebuild your distribution::

    p4a clean_recipe_build RECIPENAME
    p4a clean_dists
    # then rebuild your distribution

You can write "private" recipes for your application, just create a
``p4a-recipes`` folder in your build directory, and place a recipe in
it (edit the ``__init__.py``)::

    mkdir -p p4a-recipes/myrecipe
    touch p4a-recipes/myrecipe/__init__.py

Distribution management
~~~~~~~~~~~~~~~~~~~~~~~

Every time you start a new project, python-for-android will internally
create a new distribution (an Android build project including Python
and your other dependencies compiled for Android), according to the
requirements you added on the command line. You can force the reuse of
an existing distribution by adding::

   p4a apk --dist_name=myproject ...

This will ensure your distribution will always be built in the same
directory, and avoids using more disk space every time you adjust a
requirement.

You can list the available distributions::

    p4a distributions

And clean all of them::

    p4a clean_dists

Configuration file
~~~~~~~~~~~~~~~~~~

python-for-android checks in the current directory for a configuration
file named ``.p4a``. If found, it adds all the lines as options to the
command line. For example, you can add the options you would always
include such as::

    --dist_name my_example
    --android_api 27
    --requirements kivy,openssl

Overriding recipes sources
~~~~~~~~~~~~~~~~~~~~~~~~~~

You can override the source of any recipe using the
``$P4A_recipename_DIR`` environment variable. For instance, to test
your own Kivy branch you might set::

    export P4A_kivy_DIR=/home/username/kivy

The specified directory will be copied into python-for-android instead
of downloading from the normal url specified in the recipe.

setup.py file (experimental)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your application is also packaged for desktop using `setup.py`,
you may want to use your `setup.py` instead of the
``--requirements`` option to avoid specifying things twice.
For that purpose, check out :doc:`distutils`

Going further
~~~~~~~~~~~~~

See the other pages of this doc for more information on specific topics:

- :doc:`buildoptions`
- :doc:`commands`
- :doc:`recipes`
- :doc:`bootstraps`
- :doc:`apis`
- :doc:`troubleshooting`
- :doc:`contribute`
