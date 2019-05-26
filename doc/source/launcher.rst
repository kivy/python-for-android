.. _launcher:

Launcher
========

The Kivy Launcher is an Android application that can run any Kivy app
stored in the `kivy` folder on the SD Card. You can download the latest stable
version for your android device from the
`Play Store <https://play.google.com/store/apps/details?id=org.kivy.pygame>`_.

The stable launcher comes with various Python packages and
permissions, usually listed in the description in the store. Those
aren't always enough for an application to run or even launch if you
work with other dependencies that are not packaged.

The Kivy Launcher is intended for quick and simple testing. For
anything more advanced we recommend building your own APK with
python-for-android.

Building
--------

The Kivy Launcher is built using python-for-android. To get the most recent
versions of packages you need to clean them first, so that the packager won't
grab an old (cached) package instead of a fresh one.

.. highlight:: none

::

    p4a clean_download_cache requirements
    p4a clean_dists && p4a clean_builds
    p4a apk --requirements=requirements \
            --permission PERMISSION \
            --package=the.package.name \
            --name="App name" \
            --version=x.y.z \
            --android_api XY \
            --bootstrap=sdl2 \
            --launcher \
            --minsdk 13

.. note::

    `--minsdk 13` is necessary for the new toolchain, otherwise you'll be able
    to run apps only in `landscape` orientation.

.. warning::

    Do not use any of `--private`, `--public`, `--dir` or other arguments for
    adding `main.py` or `main.pyo` to the app. The argument `--launcher` is
    above them and tells the p4a to build the launcher version of the APK.

Usage
-----

Once the launcher is installed, you need to create a folder in your
external storage directory (e.g. ``/storage/emulated/0`` or
``/sdcard``) - this is normally your 'home' directory in a file
browser. Each new folder inside `kivy` represents a
separate application::

    /sdcard/kivy/<yourapplication>

Each application folder must contain an
`android.txt` file. The file has to contain three basic
lines::

    title=<Application Title>
    author=<Your Name>
    orientation=<portrait|landscape>

The file is editable so you can change for example orientation or
name. These are the only options dynamically configurable here,
although when the app runs you can call the Android API with PyJNIus
to change other settings.

After you set your `android.txt` file, you can now run the launcher
and start any available app from the list.

To differentiate between apps in ``/sdcard/kivy``, you can include an icon
named ``icon.png`` in the folder. The icon should be a square.

Release on the market
---------------------

Launcher is released on Google Play with each new Kivy stable
branch. The master branch is not suitable for a regular user because
it changes quickly and needs testing.

Source code
-----------

.. |kivy| replace:: sdl2 org.kivy.android

.. _sdl2:
    https://github.com/kivy/python-for-android/tree/master/\
    pythonforandroid/bootstraps/sdl2/build/src/org/kivy/android

If you feel confident, feel free to improve the launcher. You can find the
source code at |renpy|_ or at |kivy|_.
