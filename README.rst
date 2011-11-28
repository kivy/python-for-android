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
| PGS4A              | Yes           | Yes           | Yes            | No           |
| Android scripting  | No            | No            | No             | No           |
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

After installing them, export both installation path::

    export ANDROIDSDK=/path/to/android-sdk
    export ANDROIDNDK=/path/to/android-ndk

    # examples
	export ANDROIDSDK="/home/tito/code/android/android-sdk-linux_86"
	export ANDROIDNDK="/home/tito/code/android/android-ndk-r5b"


Usage
-----

Step 1, compile the toolchain::

    MODULES="openssl pygame" ./configure.sh

Step 2, package your application::

    ...


Related project
---------------

- PGS4A: http://pygame.renpy.org/
- Android scripting: http://code.google.com/p/android-scripting/
- Python on a chip: http://code.google.com/p/python-on-a-chip/
