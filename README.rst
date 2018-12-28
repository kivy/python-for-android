python-for-android
==================

|Build Status|

.. |Build Status| image:: https://secure.travis-ci.org/kivy/python-for-android.png?branch=master
   :target: https://travis-ci.org/kivy/python-for-android

python-for-android is a packager for Python apps on Android. You can
create your own Python distribution including the modules and
dependencies you want, and bundle it in an APK along with your own code.

Features include:

-  Support for building with both Python 2 and Python 3.
-  Different app backends including Kivy, PySDL2, and a WebView with
   Python webserver.
-  Automatic support for most pure Python modules, and built in support
   for many others, including popular dependencies such as numpy and
   sqlalchemy.
-  Multiple architecture targets, for APKs optimised on any given
   device.

For documentation and support, see:

-  Website: http://python-for-android.readthedocs.io
-  Mailing list: https://groups.google.com/forum/#!forum/kivy-users or
   https://groups.google.com/forum/#!forum/python-android.

In 2015 these tools were rewritten to provide a new, easier to use and
extend interface. If you are looking for the old toolchain with
distribute.sh and build.py, it is still available at
https://github.com/kivy/python-for-android/tree/old\_toolchain, and
issues and PRs relating to this branch are still accepted. However, the
new toolchain contains all the same functionality via the built in
pygame bootstrap.

In the last quarter of 2018 the python recipes has been changed, the new recipe
for python3 (3.7.1) has a new build system which has been applied to the ancient
python recipe, allowing us to bump the python2 version number to 2.7.15. This
change, unifies the build process for both python recipes, and probably solve
some issues detected over the years, but unfortunately, this change breaks the
pygame bootstrap (in a near future we will fix it or remove it). Also should be
mentioned that the old python recipe is still usable, and has been renamed to
`python2legacy`. This `python2legacy` recipe allow us to build with a minimum
api lower than 21, which is not the case for the new python recipes which are
limited to a minimum api of 21. All this work has been done using android ndk
version r17c, and your build should success with that version...but be aware
that the project is in constant development so...the ndk version will change
at some time.

Those mentioned changes has been done this way to make easier the transition
between python3 and python2. We will slowly phase out python2 support
towards 2020...so...if you are using python2 in your projects you should
consider to migrate it into python3.

Documentation
=============

Follow the `quickstart
instructions <https://python-for-android.readthedocs.org/en/latest/quickstart/>`__
to install and begin creating APKs.

Quick instructions to start would be::

    pip install python-for-android

or to test the master branch::

    pip install git+https://github.com/kivy/python-for-android.git

The executable is called ``python-for-android`` or ``p4a`` (both are
equivalent). To test that the installation worked, try::

    python-for-android recipes

This should return a list of recipes available to be built.

To build any distributions, you need to set up the Android SDK and NDK
as described in the documentation linked above.

If you did this, to build an APK with SDL2 you can try e.g.::

    p4a apk --requirements=kivy --private /home/asandy/devel/planewave_frozen/ --package=net.inclem.planewavessdl2 --name="planewavessdl2" --version=0.5 --bootstrap=sdl2

For full instructions and parameter options, see `the
documentation <https://python-for-android.readthedocs.io/en/latest/quickstart/#usage>`__.

Support
=======

If you need assistance, you can ask for help on our mailing list:

-  User Group: https://groups.google.com/group/kivy-users
-  Email: kivy-users@googlegroups.com

We also have `#support Discord channel <https://chat.kivy.org/>`_.

Contributing
============

We love pull requests and discussing novel ideas. Check out our
`contribution guide <http://kivy.org/docs/contribute.html>`__ and feel
free to improve python-for-android.

The following mailing list and IRC channel are used exclusively for
discussions about developing the Kivy framework and its sister projects:

-  Dev Group: https://groups.google.com/group/kivy-dev
-  Email: kivy-dev@googlegroups.com

We also have `#dev Discord channel <https://chat.kivy.org/>`_.

License
=======

python-for-android is released under the terms of the MIT License.
Please refer to the LICENSE file.
