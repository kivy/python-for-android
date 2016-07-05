.. _launcher:

Launcher
========

.. note::

    This form of packaging creates an APK that allows quick and dirty testing
    of your android applications. Do not use in production!

.. warning::

    Using the launcher in production gives the end-user easy access to your
    source code.

The Kivy Launcher is an Android application that can run any Kivy app
stored in `kivy` folder on SD Card. You can download the latest stable
version for your android device from the
`Play Store <https://play.google.com/store/apps/details?id=org.kivy.pygame>`_.

The stable launcher comes with various packages usually listed in the
description in the store. Those aren't always enough for an application to run
or even launch if you work with other dependencies that are not packaged.

Permissions
-----------

The stable launcher has these permissions:

 - ACCESS_COARSE_LOCATION
 - ACCESS_FINE_LOCATION
 - BLUETOOTH
 - INTERNET
 - READ_EXTERNAL_STORAGE
 - RECORD_AUDIO
 - VIBRATE
 - WRITE_EXTERNAL_STORAGE

.. |perm_docs| replace:: android documentation

.. _perm_docs:
    https://developer.android.com/guide/topics/security/permissions.html

Check the other available permissions in the |perm_docs|_.

Packages
--------

The launcher by default provides access to these packages:

 - audiostream
 - cymunk
 - docutils
 - ffmpeg
 - kivy
 - lxml
 - openssl
 - pil
 - plyer
 - pygments
 - pyjnius
 - pyopenssl
 - sqlite3
 - twisted

Building
--------

To keep up with the most recent Kivy and be able to run more than one app
without building over and over a launcher with kivy `master` branch together
with additional packager most of your apps use are necessary. To build it
you'll need pygame bootstrap (launcher is not available in sdl2 yet). To get
the most recent versions of packages you need to clean them first, so that
the packager won't grab an old package instead of fresh one.

.. highlight:: none

::

    p4a clean_dists
    p4a clean_builds
    p4a apk --requirements=requirements \
            --permission PERMISSION \
            --package=the.package.name \
            --name="App name" \
            --version=x.y.z \
            --android_api XY \
            --bootstrap=pygame \
            --launcher \
            --minsdk 13

.. note::

    `--minsdk 13` is necessary for the new toolchain, otherwise you'll be able
    to run apps only in `landscape` orientation.

.. warning::

    Do not use any of `--private`, `--public`, `--dir` or other arguments for
    adding `main.py` or `main.pyo` to the app. The argument `--launcher` is
    above them and tells the p4a to build the launcher version of the APK.

The power of the launcher is in its capability to run multiple apps from
source, which means the more packages you include, the more stable your
installation will be and the less times you'll need to update it or do anything
else with it except running apps. The necessary stuff is about 6 - 8MB big and
additional packages won't increase the size that much, which is definitelly
an advantage if there are more than two apps for testing.

Usage
-----

Once the launcher is installed, you need to create a folder on your sdcard
(`/sdcard/kivy`). Each new folder inside `kivy` represents a separate
application.

::

    /sdcard/kivy/<yourapplication>

To tell the launcher to even see your application you have to have
`android.txt` file in your app's folder. The file has to contain three basic
lines::

    title=<Application Title>
    author=<Your Name>
    orientation=<portrait|landscape>

The file is editable so you can change for example orientation or name. You
aren't allowed to change permissions however, so before building the launcher
decide carefully what permissions do you need.

After you set your `android.txt` file, you can now run the launcher and start
any available app from the list.

Release on the market
---------------------

Launcher is released on Google Play with each new Kivy stable branch. Master
branch is not suitable for a regular user because it changes quickly and needs
testing.

Source code
-----------

.. |renpy| replace:: pygame org.renpy.android

.. _renpy:
    https://github.com/kivy/python-for-android/tree/master/\
    pythonforandroid/bootstraps/pygame/build/src/org/renpy/android

If you feel confident, feel free to improve the launcher. You can find the
source code at |renpy|_. Change the link if you want to contribute to other
than pygame bootstrap.
