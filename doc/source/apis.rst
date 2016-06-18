
Accessing Android APIs
======================

When writing an Android application you may want to access the normal
Android Java APIs, in order to control your application's appearance
(fullscreen, orientation etc.), interact with other apps or use
hardware like vibration and sensors.

You can access these with `Pyjnius
<http://pyjnius.readthedocs.org/en/latest/>`_, a Python library for
automatically wrapping Java and making it callable from Python
code. Pyjnius is fairly simple to use, but not very Pythonic and it
inherits Java's verbosity. For this reason the Kivy organisation also
created `Plyer <https://plyer.readthedocs.org/en/latest/>`_, which
further wraps specific APIs in a Pythonic and cross-platform way; you
can call the same code in Python but have it do the right thing also
on platforms other than Android.

Pyjnius and Plyer are independent projects whose documentation is
linked above.  See below for some simple introductory examples, and
explanation of how to include these modules in your APKs.


Using Pyjnius
-------------

Pyjnius lets you call the Android API directly from Python Pyjnius is
works by dynamically wrapping Java classes, so you don't have to wait
for any particular feature to be pre-supported.

You can include Pyjnius in your APKs by adding `pyjnius` to your build
requirements, e.g. :code:`--requirements=flask,pyjnius`. It is
automatically included in any APK containing Kivy, in which case you
don't need to specify it manually.

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

Plyer provides a much less verbose, Pythonic wrapper to
platform-specific APIs. It supports Android as well as iOS and desktop
operating systems, though plyer is a work in progress and not all
platforms support all Plyer calls yet. 

Plyer does not support all APIs yet, but you can always Pyjnius to
call anything that is currently missing.

You can include Plyer in your APKs by adding the `Plyer` recipe to
your build requirements, e.g. :code:`--requirements=plyer`. 

You should check the `Plyer documentation <Plyer_>`_ for details of all supported
facades (platform APIs), but as an example the following is how you
would achieve vibration as described in the Pyjnius section above::

    from plyer.vibrator import vibrate
    vibrate(10)  # in Plyer, the argument is in seconds

This is obviously *much* less verbose than with Pyjnius!
