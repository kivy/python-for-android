
Accessing Android APIs
======================

When writing an Android application you may want to access the normal
Android APIs, which are available in Java. It is by calling these that
you would normally accomplish everything from vibration, to opening
other applications, to accessing sensor data.

These APIs can be accessed from Python to perform all of these tasks
and many more. This is made possible by the `Pyjnius
<http://pyjnius.readthedocs.org/en/latest/>`__ module, a Python
library for automatically wrapping Java and making it callable from
Python code. This is fairly simple to use, though not very Pythonic
and inherits Java's verbosity. For this reason the Kivy organisation
also created `Plyer <https://plyer.readthedocs.org/en/latest/>`__,
which further wraps specific APIs in a Pythonic and cross-platform
way - so in fact you can call the same code in Python but have it do
the right thing also on platforms other than Android.

These are both independent projects whose documentation is linked
above, and you can check this to learn about all the things they can
do. The following sections give some simple introductory examples,
along with explanation of how to include these modules in your APKs.


Using Pyjnius
-------------

Pyjnius lets you call the Android API directly from Python. You can
include it in your APKs by adding the `pyjnius` or `pyjniussdl2`
recipes to your build requirements.


Using Plyer
-----------


