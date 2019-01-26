
Working on Android
==================

This page gives details on accessing Android APIs and managing other
interactions on Android.


Runtime permissions
-------------------

With API level >= 21, you will need to request runtime permissions
to access the SD card, the camera, and other things.

This can be done through the `android` module, just add it to
your `--requirements` (as `android`) and then use it in your app like this::

      from android.permissions import request_permission, Permission
      request_permission(Permission.WRITE_EXTERNAL_STORAGE)

The available permissions are listed here:

https://developer.android.com/reference/android/Manifest.permission


Other common tasks
------------------

Dismissing the splash screen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With the SDL2 bootstrap, the app's splash screen may be visible
longer than necessary (with your app already being loaded) due to a
limitation with the way we check if the app has properly started.
In this case, the splash screen overlaps the app gui for a short time.

To dismiss the loading screen explicitely in your code, add p4a's `android`
module to your `--requirements` and use this::

  from android import hide_loading_screen
  hide_loading_screen()

You can call it e.g. using ``kivy.clock.Clock.schedule_once`` to run it
in the first active frame of your app, or use the app build method.


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


Advanced Android API use
------------------------

`android` for Android API access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As mentioned above, the ``android`` Python module provides a simple 
wrapper around many native Android APIS, and it can be included by
adding it to your requirements, e.g. :code:`--requirements=kivy,android`.
It is not automatically included by Kivy unless you use the old (Pygame)
bootstrap.

The available functionality of this module is not separately documented.
You can read the source `on
Github
<https://github.com/kivy/python-for-android/tree/master/pythonforandroid/recipes/android/src/android>`__.

Also please note you can replicate most functionality without it using
`pyjnius`. (see below)


`Plyer` - a more comprehensive API wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plyer provides a more thorough wrapper than `android` for a much larger
area of platform-specific APIs, supporting not only Android but also
iOS and desktop operating systems.
(Though plyer is a work in progress and not all
platforms support all Plyer calls yet)

Plyer does not support all APIs yet, but you can always use Pyjnius to
call anything that is currently missing.

You can include Plyer in your APKs by adding the `Plyer` recipe to
your build requirements, e.g. :code:`--requirements=plyer`.

You should check the `Plyer documentation <Plyer_>`_ for details of all supported
facades (platform APIs), but as an example the following is how you
would achieve vibration as described in the Pyjnius section above::

    from plyer.vibrator import vibrate
    vibrate(10)  # in Plyer, the argument is in seconds

This is obviously *much* less verbose than with Pyjnius!


`Pyjnius` - raw lowlevel API access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyjnius lets you call the Android API directly from Python Pyjnius is
works by dynamically wrapping Java classes, so you don't have to wait
for any particular feature to be pre-supported.

This is particularly useful when `android` and `plyer` don't already
provide a convenient access to the API, or you need more control.

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

