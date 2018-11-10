
Getting Started
===============

Getting up and running on python-for-android (p4a) is a simple process
and should only take you a couple of minutes. We'll refer to Python
for android as p4a in this documentation.

Concepts
--------

- requirements: For p4a, your applications dependencies are
  requirements similar to the standard `requirements.txt`, but with
  one difference: p4a will search for a recipe first instead of
  installing requirements with pip.

- recipe: A recipe is a file that defines how to compile a
  requirement. Any libraries that have a Python extension *must* have
  a recipe in p4a, or compilation will fail. If there is no recipe for
  a requirement, it will be downloaded using pip.

- build: A build refers to a compiled recipe.

- distribution: A distribution is the final "build" of all your
  compiled requirements, as an Android project that can be turned
  directly into an APK. p4a can contain multiple distributions with
  different sets of requirements.

- bootstrap: A bootstrap is the app backend that will start your
  application. Your application could use SDL2 as a base, or Pygame,
  or a web backend like Flask with a WebView bootstrap. Different
  bootstraps can have different build options.


Installation
------------

Installing p4a
~~~~~~~~~~~~~~

p4a is now available on Pypi, so you can install it using pip::

    pip install python-for-android

You can also test the master branch from Github using::

    pip install git+https://github.com/kivy/python-for-android.git

Installing Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

p4a has several dependencies that must be installed:

- git
- ant
- python2
- cython (can be installed via pip)
- a Java JDK (e.g. openjdk-7)
- zlib (including 32 bit)
- libncurses (including 32 bit)
- unzip
- virtualenv (can be installed via pip)
- ccache (optional)
- autoconf (for ffpyplayer_codecs recipe)
- libtool (for ffpyplayer_codecs recipe)

On recent versions of Ubuntu and its derivatives you may be able to
install most of these with::

    sudo dpkg --add-architecture i386
    sudo apt-get update
    sudo apt-get install -y build-essential ccache git zlib1g-dev python2.7 python2.7-dev libncurses5:i386 libstdc++6:i386 zlib1g:i386 openjdk-7-jdk unzip ant ccache autoconf libtool

On Arch Linux (64 bit) you should be able to run the following to
install most of the dependencies (note: this list may not be
complete). gcc-multilib will conflict with (and replace) gcc if not
already installed. If your installation is already 32-bit, install the
same packages but without ``lib32-`` or ``-multilib``::

    sudo pacman -S jdk7-openjdk python2 python2-pip python2-kivy mesa-libgl lib32-mesa-libgl lib32-sdl2 lib32-sdl2_image lib32-sdl2_mixer sdl2_ttf unzip gcc-multilib gcc-libs-multilib

Installing Android SDK
~~~~~~~~~~~~~~~~~~~~~~

You need to download and unpack the Android SDK and NDK to a directory (let's say $HOME/Documents/):

- `Android SDK <https://developer.android.com/studio/index.html>`_
- `Android NDK <https://developer.android.com/ndk/downloads/index.html>`_

For the Android SDK, you can download 'just the command line
tools'. When you have extracted these you'll see only a directory
named ``tools``, and you will need to run extra commands to install
the SDK packages needed. 

For Android NDK, note that modern releases will only work on a 64-bit
operating system. If you are using a 32-bit distribution (or hardware),
the latest useable NDK version is r10e, which can be downloaded here:

- `Legacy 32-bit Linux NDK r10e <http://dl.google.com/android/ndk/android-ndk-r10e-linux-x86.bin>`_

First, install a platform to target (you can also replace ``19`` with
a different platform number, this will be used again later)::

  $SDK_DIR/tools/bin/sdkmanager "platforms;android-19"

Second, install the build-tools. You can use
``$SDK_DIR/tools/bin/sdkmanager --list`` to see all the
possibilities, but 26.0.2 is the latest version at the time of writing::

  $SDK_DIR/tools/bin/sdkmanager "build-tools;26.0.2"

Then, you can edit your ``~/.bashrc`` or other favorite shell to include new environment variables necessary for building on android::

    # Adjust the paths!
    export ANDROIDSDK="$HOME/Documents/android-sdk-21"
    export ANDROIDNDK="$HOME/Documents/android-ndk-r10e"
    export ANDROIDAPI="26"  # Target API version of your application
    export NDKAPI="19"  # Minimum supported API version of your application
    export ANDROIDNDKVER="r10e"  # Version of the NDK you installed

You have the possibility to configure on any command the PATH to the SDK, NDK and Android API using:

- :code:`--sdk-dir PATH` as an equivalent of `$ANDROIDSDK`
- :code:`--ndk-dir PATH` as an equivalent of `$ANDROIDNDK`
- :code:`--android-api VERSION` as an equivalent of `$ANDROIDAPI`
- :code:`--ndk-api VERSION` as an equivalent of `$NDKAPI`
- :code:`--ndk-version VERSION` as an equivalent of `$ANDROIDNDKVER`


Usage
-----

Build a Kivy application
~~~~~~~~~~~~~~~~~~~~~~~~

To build your application, you need to have a name, version, a package
identifier, and explicitly write the bootstrap you want to use, as
well as the requirements::

    p4a apk --private $HOME/code/myapp --package=org.example.myapp --name "My application" --version 0.1 --bootstrap=sdl2 --requirements=python2,kivy

This will first build a distribution that contains `python2` and `kivy`, and using a SDL2 bootstrap. Python2 is here explicitely written as kivy can work with python2 or python3.

You can also use ``--bootstrap=pygame``, but this bootstrap is deprecated for use with Kivy and SDL2 is preferred.

Build a WebView application
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build your application, you need to have a name, version, a package
identifier, and explicitly use the webview bootstrap, as
well as the requirements::

    p4a apk --private $HOME/code/myapp --package=org.example.myapp --name "My WebView Application" --version 0.1 --bootstrap=webview --requirements=flask --port=5000

You can also replace flask with another web framework.

Replace ``--port=5000`` with the port on which your app will serve a
website. The default for Flask is 5000.

Build an SDL2 based application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This includes e.g. `PySDL2
<https://pysdl2.readthedocs.io/en/latest/>`__.

To build your application, you need to have a name, version, a package
identifier, and explicitly write the sdl2 bootstrap, as well as the
requirements::

    p4a apk --private $HOME/code/myapp --package=org.example.myapp --name "My SDL2 application" --version 0.1 --bootstrap=sdl2 --requirements=your_requirements

Add your required modules in place of ``your_requirements``,
e.g. ``--requirements=pysdl2`` or ``--requirements=vispy``.

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
    --android_api 19
    --requirements kivy,openssl


Going further
~~~~~~~~~~~~~

See the other pages of this doc for more information on specific topics:

- :doc:`buildoptions`
- :doc:`commands`
- :doc:`recipes`
- :doc:`bootstraps`
- :doc:`apis`
- :doc:`troubleshooting`
- :doc:`launcher`
- :doc:`contribute`
