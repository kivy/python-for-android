# P4A experiment

This is an experimental Python for Android APK builder based on the
pythonic toolchain of kivy-ios. Broad goals are:

- Support SDL2
- Support multiple bootstraps (user-chosen java + NDK code)
- Support python3
- Support some kind of binary distribution (?)
  (including on Windows)
- Be a standalone Pypi module (?)

This is in a very early stage and is really just an experiment,
currently working to duplicate existing python-for-android
functionality. The following command will try to download and build
some recipes. It should duplicate the functionality of distribute.sh
(and you can build an apk with the result using build.py!), but the
code is currently bad and only the few essential recipes are
supported.

     python2 toolchain.py create --name=testproject --bootstrap=pygame --recipes=sdl,python2

Add the `--debug` option to any command to enable printing all the
debug information, including output of shell commands (there's a lot if it!).

# Dependencies

- Virtualenv
- Android SDK (link by setting the ANDROIDSDK environment variable)
- Android NDK (link by setting the ANDROIDNDK environment variable)
- Cython

Pip:
- appdirs
- colorama


# Known missing stuff from P4A

- Pymodules install
- Some recipes/components aren't stripped properly of doc etc.
- Downloaded file md5 and headers aren't checked
- Biglink is essential (the p4a disable option isn't implemented)
- Probably some other stuff


# Current status

Currently can build working APKs with SDL2, kivy and pyjnius. Only the
few core recipes are avilable, but kivy apps that don't need anything
more than this will work. However, there are many hacks and bugs along
the way that now need fixing. Kivy and Pyjnius need some
(undocumented) patches.

If trying to build SDL2 with other stuff, you probably need SDL_image,
SDL_ttf and SDL_mixer as these don't have recipes yet (and unlike with
p4a probably don't need to be included in this repo).

You can try running

    python2 toolchain.py create --name=testsdl2 --bootstrap=sdl2 --recipes=sdl2,python2

to get an sdl2 dist, which has its own build.py. This is at a very
early stage! The build.py only does the zipping and tarballing, and
the SDL2 activity doesn't support any customisation yet.
