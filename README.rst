Python for Android
==================

===== THE PROJECT IS NOT USABLE YET =====


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
- application should be automatically generated (Android.mk etc...)
- Python try always to import name.so, namemodule.so, name.py, name.pyo ?
- restore libpymodules.so loading to reduce the number of dlopen.
- if MODULES= change, the old build need to be cleaned
