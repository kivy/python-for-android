
Working on Android
==================

This page gives details on accessing Android APIs and managing other
interactions on Android.


Accessing Android APIs
----------------------

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

This page also documents the ``android`` module which you can include
with p4a, but this is mostly replaced by Pyjnius and is not
recommended for use in new applications.


Using Pyjnius
~~~~~~~~~~~~~

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
~~~~~~~~~~~

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


Using ``android``
~~~~~~~~~~~~~~~~~

This Cython module was used for Android API interaction with Kivy's old
interface, but is now mostly replaced by Pyjnius.

The ``android`` Python module can be included by adding it to your
requirements, e.g. :code:`--requirements=kivy,android`. It is not
automatically included by Kivy unless you use the old (Pygame)
bootstrap.

This module is not separately documented. You can read the source `on
Github
<https://github.com/kivy/python-for-android/tree/master/pythonforandroid/recipes/android/src/android>`__.

One useful facility of this module is to make
:code:`webbrowser.open()` work on Android. You can replicate this
effect without using the android module via the following
code::

    from jnius import autoclass

    def open_url(url):
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    browserIntent = Intent()
    browserIntent.setAction(Intent.ACTION_VIEW)
    browserIntent.setData(Uri.parse(url))
    currentActivity = cast('android.app.Activity', mActivity)
    currentActivity.startActivity(browserIntent)

    class AndroidBrowser(object):
        def open(self, url, new=0, autoraise=True):
            open_url(url)
        def open_new(self, url):
            open_url(url)
        def open_new_tab(self, url):
            open_url(url)

    import webbrowser
    webbrowser.register('android', AndroidBrowser, None, -1)


Working with the App lifecycle
------------------------------

Dismissing the splash screen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With the SDL2 bootstrap, the app's splash screen may not be dismissed
immediately when your app has finished loading, due to a limitation
with the way we check if the app has properly started. In this case,
the splash screen overlaps the app gui for a short time.

You can dismiss the splash screen as follows. Run this code from your
app build method (or use ``kivy.clock.Clock.schedule_once`` to run it
in the following frame)::

  from jnius import autoclass
  activity = autoclass('org.kivy.android.PythonActivity').mActivity
  activity.removeLoadingScreen()

This problem does not affect the Pygame bootstrap, as it uses a
different splash screen method.


Handling the back button
~~~~~~~~~~~~~~~~~~~~~~~~

Android phones always have a back button, which users expect to
perform an appropriate in-app function. If you do not handle it, Kivy
apps will actually shut down and appear to have crashed.

In SDL2 bootstraps, the back button appears as the escape key (keycode
27, codepoint 270). You can handle this key to perform actions when it
is pressed.

For instance, in your App class in Kivy::

    from kivy.core.window import Window

    class YourApp(App):

       def build(self):
          Window.bind(on_keyboard=self.key_input)
          return Widget() # your root widget here as normal

       def key_input(self, window, key, scancode, codepoint, modifier):
          if key == 27:
             return True  # override the default behaviour
          else:           # the key now does nothing
             return False


Pausing the App
~~~~~~~~~~~~~~~

When the user leaves an App, it is automatically paused by Android,
although it gets a few seconds to store data etc. if necessary. Once
paused, there is no guarantee that your app will run again.

With Kivy, add an ``on_pause`` method to your App class, which returns True::

  def on_pause(self):
      return True

With the webview bootstrap, pausing should work automatically.

Under SDL2, you can handle the `appropriate events <https://wiki.libsdl.org/SDL_EventType>`__ (see SDL_APP_WILLENTERBACKGROUND etc.).
