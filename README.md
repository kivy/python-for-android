# Python for Android

Python for android is a project to create your own Python distribution
including the modules you want, and create an apk including python,
libs, and your application.

These tools were recently rewritten to provide a new, easier to use
and extend interface. If you are looking for the old toolchain with
distribute.sh and build.py, it is still available at
https://github.com/kivy/python-for-android/tree/old_toolchain, and
issues and PRs relating to this branch are still accepted. However,
the new toolchain contains all the same functionality via the built in
pygame bootstrap.

For documentation and support, see:

- Website: http://python-for-android.rtfd.org/
- Mailing list: https://groups.google.com/forum/#!forum/kivy-users or
  https://groups.google.com/forum/#!forum/python-android.

Broad goals of the revamp project include:

- ✓ Replace the old toolchain with a more extensible pythonic one
- ✓ Support SDL2
- ✓ Support multiple bootstraps (user-chosen java + NDK code, e.g. for
  multiple graphics backends or non-Kivy projects)
- (WIP) Support python3 (recipe exists but crashes on android)
- (WIP) Support some kind of binary distribution, including on windows (semi-implemented, just needs finishing)
- ✓ Be a standalone Pypi module (not on pypi yet but setup.py works)
- Support multiple architectures

We are currently working to stabilise all parts of the toolchain and
add more features. Support for pygame-based APKs is almost feature
complete with the old toolchain. Testing and contributions are
welcome.

The recent replacement of the master branch with the revamp will have
rendered most/all PRs invalid. Please retarget revamp PRs on the
master branch, or PRs for the old toolchain on the old_toolchain
branch.

# Documentation

This toolchain is documented (temporarily)
[here](http://inclem.net/files/p4a_revamp_doc/). Follow the
[quickstart instructions](http://inclem.net/files/p4a_revamp_doc/quickstart.html#quickstart)
to install and begin creating APK.

Quick instructions to start would be:

    pip install git+https://github.com/kivy/python-for-android.git

The executable is called `python-for-android` or `p4a` (both are
equivalent). To test that the installation worked, try

    python-for-android recipes

This should return a list of recipes available to be built.

To build any distributions, you need to set up the Android SDK and NDK
as described in the documentation linked above.

If you did this, to build an APK with SDL2 you can try e.g.

    p4a apk --requirements=kivysdl2 --private /home/asandy/devel/planewave_frozen/ --package=net.inclem.planewavessdl2 --name="planewavessdl2" --version=0.5 --bootstrap=sdl2

For full instructions and parameter options, see the documentation
linked above.

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

The tool works, testing is welcomed. Doc is available
[here](http://inclem.net/files/p4a_revamp_doc/).

# Development notes

Original reference commit of p4a master was
7c8d4ce9db384528f7ea83e0841fe2464a558db8 - possibly some things after
this need adding to the new toolchain. Some of the major later
additons, including ctypes in the python build, have already been
merged here.
