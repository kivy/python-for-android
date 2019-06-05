On device unit tests
====================

This test app runs a set of unit tests, to help confirm that the
python-for-android build is actually working properly.

The main tests are for the recipes built in the apk. Each module (or
other tool) is at least imported and subject to some basic check.

This app is experimental, it doesn't yet support things like testing
only the requirements you ask for (so if you build with requirements
other than those specified, the tests may fail). It also has no gui
yet, the results must be checked via logcat.

Building the app
================

This app should be built using buildozer, which it also serves as a
test for::

  $ buildozer android debug

Install on an Android device::

  $ adb install -r adb install -r bin/p4aunittests-0.1-debug.apk
    # or
  $ buildozer android deploy

Run the app and check in logcat that all the tests pass::

  $ adb logcat | grep python  # or look up the adb syntax for this
