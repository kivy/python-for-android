On device unit tests
====================

This test app runs a set of unit tests, to help confirm that the
python-for-android build is actually working properly.

Also it's dynamic, because it will run one app or another depending on the
supplied recipes at build time.

It currently supports three app `modes`:
  - `kivy app` (with sdl2 bootstrap): if kivy in recipes
  - `flask app` (with webview bootstrap): if flask in recipes
  - `no gui`: if neither of above cases is taken

The main tests are for the recipes built in the apk. Each module (or
other tool) is at least imported and subject to some basic check.

This test app can be build via `setup.py` or via buildozer. In both
cases it will build a basic kivy app with a set of tests defined via the
`requirements` keyword (specified at build time).

In case that you build the `test app with no-gui`, the unittests results must
be checked via command `adb logcat` or some logging apk (you may need root
permissions in your device to use such app).

Building the app with python-for-android
========================================

You can use the provided file `setup.py`. Check our `Makefile
<https://github.com/kivy/python-for-android/blob/develop/Makefile>`__ to guess
how to build the test app, or also you can look at `testing pull requests documentation
<https://github.com/kivy/python-for-android/blob/develop/doc/source/testing_pull_requests.rst>`__,
which describes some of the methods that you can use to build the test app.

Building the app with buildozer
===============================

This app can be built using buildozer, which it also serves as a
test for::

  $ buildozer android debug

Install on an Android device::

  $ adb install -r adb install -r bin/p4aunittests-0.1-debug.apk
    # or
  $ buildozer android deploy

Run the app and check in logcat that all the tests pass::

  $ adb logcat | grep python  # or look up the adb syntax for this
