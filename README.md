# P4A experiment

This is an experimental Python for Android APK builder based on the
pythonic toolchain of kivy-ios. Broad goals are:

- Support SDL2
- Support multiple bootstraps (user-chosen java + NDK code)
- Support python3

This is in a *very* early stage and is really just an experiment,
currently working to duplicate existing python-for-android
functionality. The following command will try to download some
recipes, all that's supported right now:

     python2 toolchain.py create_android_project --name=testproject --bootstrap=pygame --recipes=sdl,python2
