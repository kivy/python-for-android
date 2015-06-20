# P4A experiment

This is an experimental Python for Android APK builder based on the
pythonic toolchain of kivy-ios. Broad goals are:

- Support SDL2
- Support multiple bootstraps (user-chosen java + NDK code)
- Support python3
- Support some kind of binary distribution (?)
  (including on Windows)
- Be a standalone Pypi module (?)

This is in a very early stage. The following command will try to
download and build some recipes. It should duplicate the functionality
of distribute.sh (and you can build an apk with the result using
build.py!), but the code is currently bad and only the few essential
recipes are supported.

     python2 toolchain.py create --name=testproject --bootstrap=pygame --recipes=sdl,python2

Add the `--debug` option to any command to enable printing all the
debug information, including output of shell commands (there's a lot if it!).

It's also now possible to build working APKs that run kivy with sdl2, but requires some manual intervention to add the SDL_{image,mixer,ttf} jni folders, and depends on patched versions of kivy and pyjnius. Adding these as recipes (and making the download automatic) is the next thing to be done. Creating an sdl2 dist would be possible with e.g.

    python2 toolchain.py create --name=testsdl2 --bootstrap=sdl2 --recipes=sdl2,python2

Like the pygame bootstrap, this makes a dist dir with a build.py. This
supports only the --private option, and you must manually run ant to
install the APK, then the app will crash at least twice on the device
before it works. This is probably a weird unpacking problem, under
investigation.

All the details here are highly preliminary; the current priority is
to get different parts of the tool basically working (even if hacky)
before going back to set technical decisions in stone.

# Dependencies

- Virtualenv
- Android SDK (link by setting the ANDROIDSDK environment variable)
- Android NDK (link by setting the ANDROIDNDK environment variable)
- Cython

Pip:
- sh
- appdirs
- colorama


# Known missing stuff from P4A

- Pymodules install
- Some recipes/components aren't stripped properly of doc etc.
- Downloaded file md5 and headers aren't checked
- Biglink is essential (the p4a disable option isn't implemented)
- Android services are not implemented at all
- Probably some other stuff


# Current status

Currently working to fully automate SDL2 dist creation by adding
required recipes and patches for kivy and pyjnius.
