Prerequisites
=============

.. warning::

    The current version is tested only on Ubuntu oneiric (11.10). If it doesn't
    work on another platform, send us patch, not bug report.

You need the minimal environment for building python. Note that other libraries
might need other tools (cython is used by some recipes, and ccache to speedup the build)::

    sudo apt-get install build-essential patch git-core ccache cython ant

You must have android SDK and NDK. You can download them at::

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


