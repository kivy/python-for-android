python-for-android
==================

[![Build Status](https://travis-ci.org/kivy/python-for-android.svg?branch=develop)](https://travis-ci.org/kivy/python-for-android)
[![Coverage Status](https://coveralls.io/repos/github/kivy/python-for-android/badge.svg?branch=develop&kill_cache=1)](https://coveralls.io/github/kivy/python-for-android?branch=develop)
[![Backers on Open Collective](https://opencollective.com/kivy/backers/badge.svg)](#backers)
[![Sponsors on Open Collective](https://opencollective.com/kivy/sponsors/badge.svg)](#sponsors)

python-for-android is a packaging tool for Python apps on Android. You can
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

## Documentation

Follow the [quickstart
instructions](<https://python-for-android.readthedocs.org/en/latest/quickstart/>)
to install and begin creating APKs.

**Quick instructions**: install python-for-android with:

    pip install python-for-android

(for the develop branch: `pip install git+https://github.com/kivy/python-for-android.git`)

Test that the install works with:

    p4a --version

To build any actual apps, **set up the Android SDK and NDK**
as described in the [quickstart](
<https://python-for-android.readthedocs.org/en/latest/quickstart/#installing-android-sdk>).
**Use the SDK/NDK API level & NDK version as in the quickstart,**
other API levels may not work.

With everything installed, build an APK with SDL2 with e.g.:

    p4a apk --requirements=kivy --private /home/username/devel/planewave_frozen/ --package=net.inclem.planewavessdl2 --name="planewavessdl2" --version=0.5 --bootstrap=sdl2

**For full instructions and parameter options,** see [the
documentation](https://python-for-android.readthedocs.io/en/latest/quickstart/#usage).

## Support

If you need assistance, you can ask for help on our mailing list:

-  User Group: https://groups.google.com/group/kivy-users
-  Email: kivy-users@googlegroups.com

We also have [#support Discord channel](https://chat.kivy.org/).

## Contributing

We love pull requests and discussing novel ideas. Check out the Kivy
project [contribution guide](http://kivy.org/docs/contribute.html) and
feel free to improve python-for-android.

See [our
documentation](https://python-for-android.readthedocs.io/en/latest/contribute/)
for more information about the python-for-android development and
release model, but don't worry about the details. You just need to
make a pull request, we'll take care of the rest.

The following mailing list and IRC channel are used exclusively for
discussions about developing the Kivy framework and its sister projects:

-  Dev Group: https://groups.google.com/group/kivy-dev
-  Email: kivy-dev@googlegroups.com

We also have [#dev Discord channel](https://chat.kivy.org/).

## License

python-for-android is released under the terms of the MIT License.
Please refer to the LICENSE file.

## History

In 2015 these tools were rewritten to provide a new, easier-to-use and
easier-to-extend interface. If you'd like to browse the old toolchain, its
status is recorded for posterity at at
https://github.com/kivy/python-for-android/tree/old_toolchain.

In the last quarter of 2018 the python recipes were changed. The
new recipe for python3 (3.7.1) had a new build system which was
applied to the ancient python recipe, allowing us to bump the python2
version number to 2.7.15. This change unified the build process for
both python recipes, and probably solved various issues detected over the
years. It should also be mentioned that these **unified python recipes**
require a **minimum target api level of 21**,
*Android 5.0 - Lollipop*, so in the case that you need to build targeting an
api level below 21, you should use an older version of python-for-android
(<=0.7.1).

Be aware that this project is in constant development so, as per time of writing,
you should use a minimum on Android's NDK r19, and ``we recommend using NDK r19b``.
This is because the toolchains installed by
default with the NDK can be used *in-place* and the python-for-android project
has been adapted for that feature. Also be aware that more recent versions of the
Android's NDK may not work.

Those mentioned changes has been done this way to make easier the transition
between python3 and python2. We will slowly phase out python2 support
towards 2020...so...if you are using python2 in your projects you should
consider migrating it into python3.

## Contributors

This project exists thanks to all the people who contribute. [[Contribute](CONTRIBUTING.md)].
<a href="https://github.com/kivy/python-for-android/graphs/contributors"><img src="https://opencollective.com/kivy/contributors.svg?width=890&button=false" /></a>


## Backers

Thank you to all our backers! 🙏 [[Become a backer](https://opencollective.com/kivy#backer)]

<a href="https://opencollective.com/kivy#backers" target="_blank"><img src="https://opencollective.com/kivy/backers.svg?width=890"></a>


## Sponsors

Support this project by becoming a sponsor. Your logo will show up here with a link to your website. [[Become a sponsor](https://opencollective.com/kivy#sponsor)]

<a href="https://opencollective.com/kivy/sponsor/0/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/0/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/1/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/1/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/2/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/2/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/3/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/3/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/4/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/4/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/5/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/5/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/6/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/6/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/7/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/7/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/8/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/8/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/9/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/9/avatar.svg"></a>
