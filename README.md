# python-for-android revamp

This is an experimental Python for Android APK builder based on the
pythonic toolchain of kivy-ios. It is intended to replace the current
python-for-android toolchain, but to be significantly better. Broad goals include:

- ✓ Replace the old toolchain with a more extensible pythonic one
- ✓ Support SDL2
- ✓ Support multiple bootstraps (user-chosen java + NDK code, e.g. for
  multiple graphics backends or non-Kivy projects)
- (WIP) Support python3 (recipe exists but crashes on android)
- (WIP) Support some kind of binary distribution, including on windows (semi-implemented, just needs finishing)
- ✓ Be a standalone Pypi module (not on pypi yet but setup.py works)
- Support multiple architectures

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

# Known missing stuff from P4A

Relating to all bootstraps:
- Some recipes/components aren't stripped properly of doc etc.
- Some command line options of distribute.sh
- Biglink is essential (the p4a disable option isn't implemented)

Relating to SDL2 only:
- Downloaded file md5 and headers aren't checked
- Android services are not implemented at all
- App loading screen
- Public dir installation
- Keyboard height getter
- Billing support
- Kivy Launcher build (can now be implemented as a bootstrap...maybe?)
- Several build options for build.py
- Probably some other stuff

Here are some specific things relating to changes in p4a itself since
the reference commit that the revamp is based on:

# Current status

The tool works, testing is welcomed. Doc is available [here](http://inclem.net/files/p4a_revamp_doc/).

# Development notes

Original reference commit of p4a master was
7c8d4ce9db384528f7ea83e0841fe2464a558db8 - possibly some things after
this need adding to the new toolchain. One of the major later
additons, including ctypes in the python build, has already been
merged here.
