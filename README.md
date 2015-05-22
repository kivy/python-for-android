# P4A experiment

This is an experimental Python for Android APK builder based on the
pythonic toolchain of kivy-ios. Broad goals are:

- Support SDL2
- Support multiple bootstraps (user-chosen java + NDK code)
- Support python3
- Be a standalone Pypi module (?)

This is in a very early stage and is really just an experiment,
currently working to duplicate existing python-for-android
functionality. The following command will try to download and build
some recipes. It should duplicate the functionality of distribute.sh
(and you can build an apk with the result using build.py!), but the
code is currently bad and only the few essential recipes are
supported.

     python2 toolchain.py create_android_project --name=testproject --bootstrap=pygame --recipes=sdl,python2


# Dependencies

Virtualenv
Android SDK (link by setting the ANDROIDSDK environment variable)
Android NDK (link by setting the ANDROIDSDK environment variable)
Cython

Pip:
- appdirs
- colorama
