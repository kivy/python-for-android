
Accessing Android APIs
======================

When writing an Android application you may want to access the normal
Android APIs, which are available in Java. It is by calling these that
you would normally accomplish everything from vibration, to opening
other applications, to accessing sensor data.

These APIs can be accessed from Python to perform all of these tasks
and many more. This is made possible by the `Pyjnius
<http://pyjnius.readthedocs.org/en/latest/>`_ module, a Python
library for automatically wrapping Java and making it callable from
Python code. This is fairly simple to use, though not very Pythonic
and inherits Java's verbosity. For this reason the Kivy organisation
also created `Plyer <https://plyer.readthedocs.org/en/latest/>`_,
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
recipes to your build requirements (the former works with Pygame/SDL1,
the latter with SDL2, the need to make this choice will be removed
later when pyjnius internally supports multiple Android backends). It
is automatically included in any APK containing Kivy, in which case
you don't need to specify it manually.

The basic mechanism of Pyjnius is the `autoclass` command, which wraps
a Java class. For instance, here is the code to vibrate your device::

     from jnius import autoclass
     
     # We need a reference to the Java activity running the current
     # application, this reference is stored automatically by
     # Kivy's PythonActivity bootstrap

     # This one works with Pygame
     # PythonActivity = autoclass('org.renpy.android.PythonActivity')
     
     # This one works with SDL2
     PythonActivity = autoclass('org.kivy.android.PythonActivity')

     activity = PythonActivity.mActivity

     Context = autoclass('android.content.Context')
     vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)

     vibrator.vibrate(10000)  # the argument is in milliseconds
     
Things to note here are:

- The class that must be wrapped depends on the bootstrap. This is
  because Pyjnius is using the bootstrap's java source code to get a
  reference to the current activity, which both the Pygame and SDL2
  bootstraps store in the ``mActivity`` static variable. This
  difference isn't always important, but it's important to know about.
- The code closely follows the Java API - this is exactly the same set
  of function calls that you'd use to achieve the same thing from Java
  code.
- This is quite verbose - it's a lot of lines to achieve a simple
  vibration!
  
These emphasise both the advantages and disadvantage of Pyjnius; you
*can* achieve just about any API call with it (though the syntax is
sometimes a little more involved, particularly if making Java classes
from Python code), but it's not Pythonic and it's not short. These are
problems that Plyer, explained below, attempts to address.

You can check the `Pyjnius documentation <Pyjnius_>`_ for further details.


Using Plyer
-----------


