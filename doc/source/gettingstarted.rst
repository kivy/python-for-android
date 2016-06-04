Getting Started
===============

Getting up and running on Python for android is a simple process and should only take you a couple of minutes. We'll refer to Python for android as P4A in this documentation.

Concepts
--------

- requirements: For P4A, your applications dependencies are requirements that looks like `requirements.txt`, in one difference: P4A will search a recipe first instead of installing requirements with pip.

- recipe: A recipe is a file that define how to compile a requirement. Any libraries that have a Python Extension MUST have a recipe in P4A. If there is no recipe for a requirement, it will be downloaded using pip.

- build: A build is referring to a compiled recipe.

- distribution: A distribution is the final "build" of all your requirements

- bootstrap: A bootstrap is a "base" that will "boot" your application. Your application could boot on a project that use SDL2 as a base, or pygame, or a pure python web. The bootstrap you're using might behave differently.


Installation
------------

Installing P4A
~~~~~~~~~~~~~~

P4A is not yet released on Pypi, but you can install it using pip::

    pip install git+https://github.com/kivy/python-for-android.git

Installing Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

P4A has several dependencies that must be installed:

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

On recent versions of Ubuntu and its derivatives you may be able to
install most of these with::

    sudo dpkg --add-architecture i386
    sudo apt-get update
    sudo apt-get install -y build-essential ccache git zlib1g-dev python2.7 python2.7-dev libncurses5:i386 libstdc++6:i386 zlib1g:i386 openjdk-7-jdk unzip ant ccache

Installing Android SDK
~~~~~~~~~~~~~~~~~~~~~~

You need to download and unpack to a directory (let's say $HOME/Documents/):

- `Android SDK <https://developer.android.com/sdk/index.html#Other>`_
- `Android NDK <https://developer.android.com/ndk/downloads/index.html>`_

Then, you can edit your `~/.bashrc` or others favorite shell to include new environment variables necessary for building on android::

    # Adjust the paths!
    export ANDROIDSDK="$HOME/Documents/android-sdk-21"
    export ANDROIDNDK="$HOME/Documents/android-ndk-r10e"
    export ANDROIDAPI="14"  # Minimum API version your application require
    export ANDROIDNDKVER="r10e"  # Version of the NDK you installed

You have the possibility to configure on any command the PATH to the SDK, NDK and Android API using:

- `--sdk_dir PATH` as an equivalent of `$ANDROIDSDK`
- `--ndk_dir PATH` as an equivalent of `$ANDROIDNDK`
- `--android_api VERSION` as an equivalent of `$ANDROIDAPI`
- `--ndk_ver PATH` as an equivalent of `$ANDROIDNDKVER`


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
~~~~~~~~~~~~~~~~~~~~~~~~~

To build your application, you need to have a name, version, a package
identifier, and explicitly use the webview bootstrap, as
well as the requirements::

    p4a apk --private $HOME/code/myapp --package=org.example.myapp --name "My WebView Application" --version 0.1 --bootstrap=webview --requirements=flask --port=5000

You can also replace flask with another web framework.

Replace ``--port=5000`` with the port your app will serve a website
on. The default for Flask is 5000.

Build an SDL2 based application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This includes `Vispy <http://vispy.org/>`__ and `PySDL2
<https://pysdl2.readthedocs.io/en/latest/>`__.

To build your application, you need to have a name, version, a package
identifier, and explicitly write the sdl2 bootstrap, as well as the
requirements::

    p4a apk --private $HOME/code/myapp --package=org.example.myapp --name "My SDL2 application" --version 0.1 --bootstrap=sdl2 --requirements=your_requirements

Add your required modules in place of ``your_requirements``,
e.g. ``--requirements=pysdl2`` or ``--requirements=vispy``.
    

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
group <https://groups.google.com/forum/#!forum/kivy-users>`__ or irc
channel #kivy at irc.freenode.net .

See :ref:`Troubleshooting <troubleshooting>` for more information.


Advanced usage
--------------

Recipe management
~~~~~~~~~~~~~~~~~~

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
    

Distributions management
~~~~~~~~~~~~~~~~~~~~~~~~

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

Going further
-------------




P4A is capable of a lot like:

- Using a configuration file to prevent you typing all the options everytime
- ...
