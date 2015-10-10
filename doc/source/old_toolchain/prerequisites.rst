Prerequisites
-------------

.. note:: There is a VirtualBox Image we provide with the
    prerequisites along with the Android SDK and NDK preinstalled to
    ease your installation woes. You can download it from `here
    <http://kivy.org/#download>`__.

.. warning::

    The current version is tested only on Ubuntu oneiric (11.10) and
    precise (12.04). If it doesn't work on other platforms, send us a
    patch, not a bug report. Python for Android works on Linux and Mac
    OS X, not Windows.

You need the minimal environment for building python. Note that other
libraries might need other tools (cython is used by some recipes, and
ccache to speedup the build)::

    sudo apt-get install build-essential patch git-core ccache ant python-pip python-dev

If you are on a 64 bit distro, you should install these packages too ::

    sudo apt-get install ia32-libs  libc6-dev-i386

On debian Squeeze amd64, those packages were found to be necessary ::

    sudo apt-get install lib32stdc++6 lib32z1

Ensure you have the latest Cython version::

    pip install --upgrade cython

You must have android SDK and NDK. The SDK defines the Android
functions you can use.  The NDK is used for compilation. Right now,
it's preferred to use:

- SDK API 8 or 14 (15 will only work with a newly released NDK)
- NDK r5b or r7

You can download them at::

    http://developer.android.com/sdk/index.html
    http://developer.android.com/sdk/ndk/index.html


In general, Python for Android currently works with Android 2.3 to L.

If it's your very first time using the Android SDK, don't forget to
follow the documentation for recommended components at::

    http://developer.android.com/sdk/installing/adding-packages.html

        You need to download at least one platform into your environment, so
        that you will be able to compile your application and set up an Android
        Virtual Device (AVD) to run it on (in the emulator). To start with,
        just download the latest version of the platform. Later, if you plan to
        publish your application, you will want to download other platforms as
        well, so that you can test your application on the full range of
        Android platform versions that your application supports.

After installing them, export both installation paths, NDK version,
and API to use::

    export ANDROIDSDK=/path/to/android-sdk
    export ANDROIDNDK=/path/to/android-ndk
    export ANDROIDNDKVER=rX
    export ANDROIDAPI=X

    # example
    export ANDROIDSDK="/home/tito/code/android/android-sdk-linux_86"
    export ANDROIDNDK="/home/tito/code/android/android-ndk-r7"
    export ANDROIDNDKVER=r7
    export ANDROIDAPI=14

Also, you must configure your PATH to add the ``android`` binary::

    export PATH=$ANDROIDNDK:$ANDROIDSDK/platform-tools:$ANDROIDSDK/tools:$PATH

