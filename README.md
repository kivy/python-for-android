# python-for-android revamp

This is an experimental Python for Android APK builder based on the
pythonic toolchain of kivy-ios. It is intended to replace the current
python-for-android toolchain, but to be significantly better. Broad goals include:

- Replace the old toolchain with a more extensible pythonic one
- Support SDL2
- Support multiple bootstraps (user-chosen java + NDK code, e.g. for
  multiple graphics backends or non-Kivy projects)
- Support python3
- Support some kind of binary distribution
  (including on Windows)
- Be a standalone Pypi module

This is at an early (but working!) stage; the new toolchain has been
fully written (save for clearing up bugs and non-essential features),
and the toolchain supports both SDL2 and Pygame backends. The other
features will be tackled soon.

We are currently working to stabilise all parts of the toolchain and
add more features. Testing is welcome.

# Documentation

This toolchain is documented (temporarily)
[here](http://inclem.net/files/p4a_revamp_doc/).

Quick instructions to start would be:

    pip install git+https://github.com/kivy/python-for-android.git@revamp

The executable is called `python-for-android` or `p4a` (both are
equivalent). To test that the installation worked, try

    python-for-android recipes

This should return a list of recipes available to be built.

To build any distributions, you need to set up the Android SDK and NDK
as described in the documentation linked above.

If you did this, to build an APK with SDL2 you can try e.g.

    p4a apk --requirements=kivysdl2 --private /home/asandy/devel/planewave_frozen/ --package=net.inclem.planewavessdl2 --name="planewavessdl2" --version=0.5 --bootstrap=sdl2

This may currently fail, the api is being sorted out. If it works, the
apk will be returned in the current directory. The full dist will be
built the first time (taking several minutes) but not subsequent
times.


# Dependencies

This list is not exhaustive. Where possible, these are not installed
automatically by pip.

- Virtualenv
- Android SDK (link by setting the ANDROIDSDK environment variable)
- Android NDK (link by setting the ANDROIDNDK environment variable)
- Cython

Pip:
- sh
- appdirs
- colorama
- jinja2


# Known missing stuff from P4A

This list relates only to the SDL2 bootstrap unless stated otherwise -
the pygame version has many of them implemented internally

- Pymodules install (all bootstraps)
- Public dir installation
- Some recipes/components aren't stripped properly of doc etc. (all bootstraps)
- Downloaded file md5 and headers aren't checked
- Some command line options of distribute.sh
- Biglink is essential (the p4a disable option isn't implemented)
- Android services are not implemented at all
- App loading screen
- Billing support
- Kivy Launcher build (can now be implemented as a bootstrap...maybe?)
- Several build options for build.py
- Probably some other stuff

# Untested recipes

These recipes exist and probably should work, but haven't been
properly tested (if at all).

- vispy
- numpy


# Current status

Working to make some kind of alpha release.
