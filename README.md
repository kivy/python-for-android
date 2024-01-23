# python-for-android

python-for-android (p4a) is a development tool that packages Python apps into
binaries that can run on Android devices.

It can generate: 

* [Android Package](https://en.wikipedia.org/wiki/Apk_(file_format)) (APK)
  files, ready to install locally on a device, especially for testing. This format
  is used by many [app stores](https://en.wikipedia.org/wiki/List_of_Android_app_stores)
  but not [Google Play Store](https://play.google.com/store/). 
* [Android App Bundle](https://developer.android.com/guide/app-bundle/faq) 
  (AAB) files which can be shared on [Google Play Store](https://play.google.com/store/).
* [Android Archive](https://developer.android.com/studio/projects/android-library)
  (AAR) files which can be used as a re-usable bundle of resources for other 
  projects.
 
It supports multiple CPU architectures.

It supports apps developed with [Kivy framework](http://kivy.org), but was
built to be flexible about the backend libraries (through "bootstraps"), and 
also supports [PySDL2](https://pypi.org/project/PySDL2/), and a
[WebView](https://developer.android.com/reference/android/webkit/WebView) with
a Python web server.

It automatically supports dependencies on most pure Python packages. For other
packages, including those that depend on C code, a special "recipe" must be 
written to support cross-compiling. python-for-android comes with recipes for
many of the mosty popular libraries (e.g. numpy and sqlalchemy) built in.

python-for-android works by cross-compiling the Python interpreter and its
dependencies for Android devices, and bundling it with the app's python code
and dependencies. The Python code is then interpreted on the Android device.

It is recommended that python-for-android be used via 
[Buildozer](https://buildozer.readthedocs.io/), which ensures the correct
dependencies are pre-installed, and centralizes the configuration. However, 
python-for-android is not limited to being used with Buildozer.

[![Backers on Open Collective](https://opencollective.com/kivy/backers/badge.svg)](#backers)
[![Sponsors on Open Collective](https://opencollective.com/kivy/sponsors/badge.svg)](#sponsors)
[![GitHub contributors](https://img.shields.io/github/contributors-anon/kivy/python-for-android)](https://github.com/kivy/python-for-android/graphs/contributors)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

![PyPI - Version](https://img.shields.io/pypi/v/python-for-android)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/python-for-android)

[![Unit tests & build apps](https://github.com/kivy/python-for-android/workflows/Unit%20tests%20&%20build%20apps/badge.svg?branch=develop)](https://github.com/kivy/python-for-android/actions?query=workflow%3A%22Unit+tests+%26+build+apps%22)
[![Coverage Status](https://coveralls.io/repos/github/kivy/python-for-android/badge.svg?branch=develop&kill_cache=1)](https://coveralls.io/github/kivy/python-for-android?branch=develop)

## Documentation

More information is available in the 
[online documentation](https://python-for-android.readthedocs.io) including a
[quickstart guide](https://python-for-android.readthedocs.io/en/latest/quickstart/).

python-for-android is managed by the [Kivy team](https://kivy.org).

## Support

Are you having trouble using python-for-android or any of its related projects
in the Kivy ecosystem?
Is there an error you don’t understand? Are you trying to figure out how to use 
it? We have volunteers who can help!

The best channels to contact us for support are listed in the latest 
[Contact Us](https://github.com/kivy/pyton-for-android/blob/master/CONTACT.md)
document.

## Code of Conduct

In the interest of fostering an open and welcoming community, we as 
contributors and maintainers need to ensure participation in our project and 
our sister projects is a harassment-free and positive experience for everyone. 
It is vital that all interaction is conducted in a manner conveying respect, 
open-mindedness and gratitude.

Please consult the [latest Code of Conduct](https://github.com/kivy/python-for-android/blob/master/CODE_OF_CONDUCT.md).

## Contributors

This project exists thanks to 
[all the people who contribute](https://github.com/kivy/python-for-android/graphs/contributors).
[[Become a contributor](CONTRIBUTING.md)].

<img src="https://contrib.nn.ci/api?repo=kivy/python-for-android&pages=5&no_bot=true&radius=22&cols=18">

## Backers

Thank you to [all of our backers](https://opencollective.com/kivy)! 
🙏 [[Become a backer](https://opencollective.com/kivy#backer)]

<img src="https://opencollective.com/kivy/backers.svg?width=890&avatarHeight=44&button=false">

## Sponsors

Special thanks to 
[all of our sponsors, past and present](https://opencollective.com/kivy).
Support this project by 
[[becoming a sponsor](https://opencollective.com/kivy#sponsor)].

Here are our top current sponsors. Please click through to see their websites,
and support them as they support us. 

<!--- See https://github.com/orgs/kivy/discussions/15 for explanation of this code. -->
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
