# FAQ for python-for-android (p4a)

## Introduction

[python-for-android](https://python-for-android.readthedocs.io/) is an open
source build tool to let you package Python code into standalone Android artifacts (APKs, AABs, AARs).
These can be passed around, installed, or uploaded to marketplaces such as the
Play Store just like any other Android app.

### Sibling Projects:

This tool was originally developed for apps produced with
the [Kivy framework](https://github.com/kivy/kivy), and is
managed by the same team. However, it can be used to build other types of Python
apps for Android.

p4a is often used in conjunction
with [Buildozer](https://github.com/kivy/buildozer), which can download, install
and keep up-to-date any necessary prerequisites (including p4a itself), for a
number of target platforms, using a specification file to define the build.

### Is it possible to have a kiosk app on Android?

Thomas Hansen wrote a detailed answer
on [the kivy-users mailing list](https://groups.google.com/d/msg/kivy-users/QKoCekAR1c0/yV-85Y_iAwoJ)

Basically, you need to root the device, remove the SystemUI package, add some
lines to the xml configuration, and you're done.

### Common Errors

The following are common problems and resolutions that users have reported.


#### AttributeError: ‘Context’ object has no attribute ‘hostpython’

This is a known bug in some releases. To work around it, add your python
requirement explicitly, e.g. `--requirements=python3,kivy`. This also applies
when using buildozer, in which case add python3 to your buildozer.spec
requirements.

#### linkname too long

This can happen when you try to include a very long filename, which doesn’t
normally happen but can occur accidentally if the p4a directory contains a
`.buildozer` directory that is not excluded from the build (e.g. if buildozer
was previously used). Removing this directory should fix the problem, and is
desirable anyway since you don’t want it in the APK.

#### Requested API target XX is not available, install it with the SDK android tool

This means that your SDK is missing the required platform tools. You need to
install the `platforms;android-XX` package in your SDK, using the android or
sdkmanager tools (depending on SDK version).

If using buildozer this should be done automatically, but as a workaround you
can run these from `~/.buildozer/android/platform/android-sdk-XX/tools/android`

#### SSLError(“Can’t connect to HTTPS URL because the SSL module is not available.”)
Your hostpython3 was compiled without SSL support. You need to install the SSL
development files before rebuilding the hostpython3 recipe. Remember to always
clean the build before rebuilding (`p4a clean builds`, or with buildozer `buildozer
android clean`).

On Ubuntu and derivatives:

    apt install libssl-dev
    p4a clean builds # or with: buildozer `buildozer android clean

On macOS:

    brew install openssl
    p4a clean builds # or with: buildozer `buildozer android clean
