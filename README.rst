Python for Android
==================

Python for android is a project to create your own Python distribution
including the modules you want, and create an apk including python, libs, and
your application.

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


Prerequisites
-------------

WARNING: the current version is working only on Ubuntu oneiric (11.10). We
don't provide support on other platform. If it doesn't work, send us patch, not
bug report.

You need the minimal environment for building python. Note that other libraries
might need other tools::

    sudo apt-get install build-essential patch

You must have android SDK and NDK. You can download them at::

    http://developer.android.com/sdk/index.html
    http://developer.android.com/sdk/ndk/index.html

If it's your very first time into android sdk, don't forget to follow
documentation for recommended components at::

    http://developer.android.com/sdk/installing.html#which

        You need to download at least one platform into your environment, so
        that you will be able to compile your application and set up an Android
        Virtual Device (AVD) to run it on (in the emulator). To start with,
        just download the latest version of the platform. Later, if you plan to
        publish your application, you will want to download other platforms as
        well, so that you can test your application on the full range of
        Android platform versions that your application supports.

After installing them, export both installation path, ndk version and api to use::

    export ANDROIDSDK=/path/to/android-sdk
    export ANDROIDNDK=/path/to/android-ndk
    export ANDROIDNDKVER=rX
    export ANDROIDAPI=X

    # example
    export ANDROIDSDK="/home/tito/code/android/android-sdk-linux_86"
    export ANDROIDNDK="/home/tito/code/android/android-ndk-r7"
    export ANDROIDNDKVER=r7
    export ANDROIDAPI=14


Usage
-----

Step 1, compile the toolchain::

    ./distribute.sh -m "kivy"

After a long time, you'll get a "dist/default" directory containing all the compiled
libraries and build.py script to package your application using thoses
libraries.

Step 2, package your application::

    cd dist/default
    ./build.py --package org.test.touchtracer --name touchtracer \
    --version 1.0 --dir ~/code/kivy/examples/demo/touchtracer installd

Example of other toolchain::

    ./distribute.sh -m "pil kivy"
    ./distribute.sh -m "openssl python"

    # create another distribution in a directory bleh
    ./distribute.sh -m "openssl kivy" -d bleh
    cd dist/bleh
    ./build.py ...

Available options::

    -d directory           Name of the distribution directory
    -h                     Show this help
    -l                     Show a list of available modules
    -m 'mod1 mod2'         Modules to include

How does it work ?
------------------

To be able to run Python on android, you need to compile it for android. And
you need to compile all the libraries you want for android too.
Since Python is a language, not a toolkit, you cannot draw any user interface
with it: you need to use a toolkit for it. Kivy can be one of them.

So for a simple ui project, the first step is to compile Python + Kivy + all
others libraries. Then you'll have what we call a "distribution".
A distribution is composed of:

- Python libraries
- All selected libraries (kivy, pygame, pil...)
- A java bootstrap
- A build script

You'll use the build script for create an "apk": an android package.


Customize your distribution
---------------------------

The basic layout of a distribution is::

    AndroidManifest.xml     - (*) android manifest (generated from templates)
    assets/
        private.mp3         - (*) fake package that will contain all the python installation
        public.mp3          - (*) fake package that will contain your application
    bin/                    - contain all the apk generated from build.py
    blacklist.txt           - list of file patterns to not include in the APK
    buildlib/               - internals libraries for build.py
    build.py                - build script to use for packaging your application
    build.xml               - (*) build settings (generated from templates)
    default.properties      - settings generated from your distribute.sh
    libs/                   - contain all the compiled libraries
    local.properties        - settings generated from your distribute.sh
    private/                - private directory containing all the python files
        lib/                  this is where you can remove or add python libs.
            python2.7/        by default, some modules are already removed (tests, idlelib, ...)
    project.properties      - settings generated from your distribute.sh
    python-install/         - the whole python installation, generated from distribute.sh
                              not included in the final package.
    res/                    - (*) android resource (generated from build.py)
    src/                    - Java bootstrap
    templates/              - Templates used by build.py

    (*): Theses files are automatically generated from build.py, don't change them directly !


Available modules
-----------------

List of available modules: jpeg pil png sdl sqlite3 pygame kivy android

The up-to-date list is available at:
https://github.com/tito/python-for-android/tree/master/recipes

Only hostpython and python are 2 mandatory recipes, used for building
hostpython / target python libraries.


Create your own recipes
-----------------------

A recipe is a script that contain the "definition" of a module to compile.
The directory layout of a recipe for a <modulename> is something like::

    python-for-android/recipes/<modulename>/recipe.sh
    python-for-android/recipes/<modulename>/patches/
    python-for-android/recipes/<modulename>/patches/fix-path.patch

When building, all the recipe build must go to::

    python-for-android/build/<modulename>/<archiveroot>

For example, if you want to create a recipe for sdl, do::

    cd python-for-android/recipes
    mkdir sdl
    cp recipe.sh.tmpl sdl/recipe.sh
    sed -i 's#XXX#sdl#' sdl/recipe.sh

Then, edit the sdl/recipe.sh to adjust other information (version, url) and
complete build function.


Related project
---------------

- PGS4A: http://pygame.renpy.org/
- Android scripting: http://code.google.com/p/android-scripting/
- Python on a chip: http://code.google.com/p/python-on-a-chip/


TODO
----

- jni/Android.mk must not include ttf/image/mixer if not asked by the user
- Python try always to import name.so, namemodule.so, name.py, name.pyo ?
- restore libpymodules.so loading to reduce the number of dlopen.
- if MODULES= change, the old build need to be cleaned
