
Bootstraps
==========

python-for-android (p4a) supports multiple *bootstraps*. These fulfil a
similar role to recipes, but instead of describing how to compile a
specific module they describe how a full Android project may be put
together from a combination of individual recipes and other
components such as Android source code and various build files.

If you do not want to modify p4a, you don't need to worry about
bootstraps, just make sure you specify what modules you want to use
(or specify an existing bootstrap manually), and p4a will
automatically build everything appropriately. 

This page describes the basics of how bootstraps work so that you can
create and use your own if you like, making it easy to build new kinds
of Python project for Android.
