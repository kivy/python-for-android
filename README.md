python-for-android
==================

[![Unit tests & build apps](https://github.com/kivy/python-for-android/workflows/Unit%20tests%20&%20build%20apps/badge.svg?branch=develop)](https://github.com/kivy/python-for-android/actions?query=workflow%3A%22Unit+tests+%26+build+apps%22)
[![Coverage Status](https://coveralls.io/repos/github/kivy/python-for-android/badge.svg?branch=develop&kill_cache=1)](https://coveralls.io/github/kivy/python-for-android?branch=develop)
[![Backers on Open Collective](https://opencollective.com/kivy/backers/badge.svg)](#backers)
[![Sponsors on Open Collective](https://opencollective.com/kivy/sponsors/badge.svg)](#sponsors)

python-for-android (p4a) is a packaging tool for Python apps on Android. You can
create your own Python distribution including the modules and
dependencies you want, and bundle it in an APK or AAB along with your own code.

Features include:

-  Different app backends including Kivy, PySDL2, and a WebView with
   Python webserver.
-  Automatic support for most pure Python modules, and built in support
   for many others, including popular dependencies such as numpy and
   sqlalchemy.
-  Multiple architecture targets, for APKs optimised on any given
   device.
-  AAB: Android App Bundle support.

python-for-android is managed by the [Kivy team](https://kivy.org).
python-for-android is perfect for Kivy apps, but is not limited to those. 

More information is available in the 
[online documentation](https://python-for-android.readthedocs.io) including a
[quickstart
guide](https://python-for-android.readthedocs.org/en/latest/quickstart/).

## Support

Are you having trouble using the Kivy framework, or any of its related projects? Is
there an error you don't understand? Are you trying to figure out how to use it? We
have volunteers who can help!

Details can be found in the latest 
[Kivy Contact page](https://kivy.org/doc/master/contact.html).

## Contributing

We welcome (and rely on)
users who want to give back to the community by contributing to the project.

Contributions can come in many forms.

Please read our latest 
[Contribution Guidelines](https://python-for-android.readthedocs.org/en/latest/contribute.html)
for more.

## License

python-for-android is released under the terms of the MIT License.
Please refer to the LICENSE file.

## History

In 2015 these tools were rewritten to provide a new, easier-to-use and
easier-to-extend interface. If you'd like to browse the old toolchain, its
status is recorded for posterity at
https://github.com/kivy/python-for-android/tree/old_toolchain.

In the last quarter of 2018 the Python recipes were changed. The
new recipe for Python3 (3.7.1) had a new build system which was
applied to the ancient Python recipe, allowing us to bump the Python2
version number to 2.7.15. This change unified the build process for
both Python recipes, and probably solved various issues detected over the
years. These **unified Python recipes** require a **minimum target api level of 21**,
*Android 5.0 - Lollipop*. If you need to build targeting an
api level below 21, you should use an older version of python-for-android
(<=0.7.1).

On March 2020 we dropped support for creating apps that use Python 2. The latest
python-for-android release that supported building Python 2 was version 2019.10.6.

On August 2021, we added support for Android App Bundle (aab). As a
collateral benefit, we now support multi-arch apk.

## Contributors

This project exists thanks to all the people who contributed. [[Become a contributor](https://kivy.org/doc/stable/contribute.html)].
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
<a href="https://opencollective.com/kivy/sponsor/10/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/10/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/11/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/11/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/12/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/12/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/13/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/13/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/14/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/14/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/15/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/15/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/16/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/16/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/17/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/17/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/18/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/18/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/19/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/19/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/20/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/20/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/21/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/21/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/22/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/22/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/23/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/23/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/24/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/24/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/25/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/25/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/26/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/26/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/27/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/27/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/28/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/28/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/29/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/29/avatar.svg"></a>
<a href="https://opencollective.com/kivy/sponsor/30/website" target="_blank"><img src="https://opencollective.com/kivy/sponsor/30/avatar.svg"></a>

