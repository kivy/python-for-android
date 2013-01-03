Python for Android
==================

Python for android is a project to create your own Python distribution
including the modules you want, and create an apk including python, libs, and
your application.

- Website: http://python-for-android.rtfd.org/
- Forum: https://groups.google.com/forum/?hl=fr#!forum/python-android
- Mailing list: python-android@googlegroups.com


Global overview
---------------

#. Download Android NDK, SDK
 
 * NDK: http://dl.google.com/android/ndk/android-ndk-r8c-linux-x86.tar.bz2
 
 * More details at: http://developer.android.com/tools/sdk/ndk/index.html
 
 * SDK: http://dl.google.com/android/android-sdk_r21.0.1-linux.tgz
 
 * More details at:http://developer.android.com/sdk/index.html

#. Launch "android", and download latest Android platform, here API 14, which would be Android 4.0

#. Export some environment variables::

    export ANDROIDSDK="/path/to/android/android-sdk-linux_86"
    export ANDROIDNDK="/path/to/android/android-ndk-r8c"
    export ANDROIDNDKVER=r8c
    export ANDROIDAPI=14

 (Of course correct the paths mentioned in ANDROIDSDK and ANDROIDNDK)

#. Clone python-for-android::

    git clone git://github.com/kivy/python-for-android

#. Build a distribution with OpenSSL module, PIL and Kivy::

    cd python-for-android
    ./distribute.sh -m "openssl pil kivy"

#. Go to your fresh distribution, build the APK of your application::

    cd dist/default
    ./build.py --package org.test.touchtracer --name touchtracer \
    --version 1.0 --dir ~/code/kivy/examples/demo/touchtracer debug

#. Install the debug apk to your device::

    adb install bin/touchtracer-1.0-debug.apk

#. Enjoy.


Troubleshooting
---------------

if you get the following message:

    Android NDK: Host 'awk' tool is outdated. Please define HOST_AWK to point to Gawk or Nawk !

a solution is to remove the "awk" binary in the android ndk distribution

    rm $ANDROIDNDK/prebuilt/linux-x86/bin/awk
