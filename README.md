# python-for-android

python-for-android is a packager for Python apps on Android. You can
create your own Python distribution including the modules and
dependencies you want, and bundle it in an APK along with your own
code.

Features include:

- Support for building with both Python 2 and Python 3.
- Different app backends including Kivy, PySDL2, and a WebView with
  Python webserver.
- Automatic support for most pure Python modules, and built in support
  for many others, including popular dependencies such as numpy and
  sqlalchemy.
- Multiple architecture targets, for APKs optimised on any given device.

For documentation and support, see:

- Website: http://python-for-android.readthedocs.io
- Mailing list: https://groups.google.com/forum/#!forum/kivy-users or
  https://groups.google.com/forum/#!forum/python-android.

In 2015 these tools were rewritten to provide a new, easier to use and
extend interface. If you are looking for the old toolchain with
distribute.sh and build.py, it is still available at
https://github.com/kivy/python-for-android/tree/old_toolchain, and
issues and PRs relating to this branch are still accepted. However,
the new toolchain contains all the same functionality via the built in
pygame bootstrap.

# Documentation

Follow the
[quickstart instructions](https://python-for-android.readthedocs.org/en/latest/quickstart/)
to install and begin creating APKs.

Quick instructions to start would be::

    pip install python-for-android

or to test the master branch::

    pip install git+https://github.com/kivy/python-for-android.git

The executable is called `python-for-android` or `p4a` (both are
equivalent). To test that the installation worked, try

    python-for-android recipes

This should return a list of recipes available to be built.

To build any distributions, you need to set up the Android SDK and NDK
as described in the documentation linked above.

If you did this, to build an APK with SDL2 you can try e.g.

    p4a apk --requirements=kivy --private /home/asandy/devel/planewave_frozen/ --package=net.inclem.planewavessdl2 --name="planewavessdl2" --version=0.5 --bootstrap=sdl2

For full instructions and parameter options, see [the documentation](https://python-for-android.readthedocs.io/en/latest/quickstart/#usage).

# Support

If you need assistance, you can ask for help on our mailing list:

* User Group: https://groups.google.com/group/kivy-users
* Email: kivy-users@googlegroups.com

We also have an IRC channel:

* Server: irc.freenode.net
* Port: 6667, 6697 (SSL only)
* Channel: #kivy

# Contributing

We love pull requests and discussing novel ideas. Check out our
[contribution guide](http://kivy.org/docs/contribute.html) and
feel free to improve python-for-android.

The following mailing list and IRC channel are used exclusively for
discussions about developing the Kivy framework and its sister projects:

* Dev Group: https://groups.google.com/group/kivy-dev
* Email: kivy-dev@googlegroups.com

IRC channel:

* Server: irc.freenode.net
* Port: 6667, 6697 (SSL only)
* Channel: #kivy or #kivy-dev

# License

python-for-android is released under the terms of the MIT License. Please refer to the
LICENSE file.
