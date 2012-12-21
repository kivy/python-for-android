Prerequisites
=============

.. note::
    There is a VirtualBox Image we provide with the prerequisites along with
    Android SDK and NDK preinstalled to ease your installation woes. You can download it from `here <http://kivy.org/#download>`__.

.. warning::

    The current version is tested only on Ubuntu oneiric (11.10) and precise
    (12.04). If it doesn't work on other platforms, send us patch, not bug
    report.

You need the minimal environment for building python. Note that other libraries
might need other tools (cython is used by some recipes, and ccache to speedup the build)::

    sudo apt-get install build-essential patch git-core ccache ant pip python-dev
 
If you are on a 64 bit distro, you should install these packages too ::

    sudo apt-get install ia32-libs and libc6-dev-i386

On debian Squeeze amd64, those packages were found to be necessary ::

    sudo apt-get install lib32stdc++6 lib32z1

Ensure you have the latest cython version::

    pip install --upgrade cython

You must have android SDK and NDK. Right now, it's prefered to use:

- SDK API 8 or 14 (15 will not work until a new NDK is released)
- NDK r5b or r7

You can download them at::

    http://developer.android.com/sdk/index.html
    http://developer.android.com/sdk/ndk/index.html

If it's your very first time into android SDK, don't forget to follow
documentation for recommended components at::

    http://developer.android.com/sdk/installing.html#which

        You need to download at least one platform into your environment, so
        that you will be able to compile your application and set up an Android
        Virtual Device (AVD) to run it on (in the emulator). To start with,
        just download the latest version of the platform. Later, if you plan to
        publish your application, you will want to download other platforms as
        well, so that you can test your application on the full range of
        Android platform versions that your application supports.

After installing them, export both installation path, NDK version and API to use::

    export ANDROIDSDK=/path/to/android-sdk
    export ANDROIDNDK=/path/to/android-ndk
    export ANDROIDNDKVER=rX
    export ANDROIDAPI=X

    # example
    export ANDROIDSDK="/home/tito/code/android/android-sdk-linux_86"
    export ANDROIDNDK="/home/tito/code/android/android-ndk-r7"
    export ANDROIDNDKVER=r7
    export ANDROIDAPI=14

Also, you must configure you're PATH to add the ``android`` binary::

    export PATH=$ANDROIDNDK:$ANDROIDSDK/tools:$PATH

