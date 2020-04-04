
Working on Android
==================

This page gives details on accessing Android APIs and managing other
interactions on Android.

Storage paths
-------------

If you want to store and retrieve data, you shouldn't just save to
the current directory, and not hardcode `/sdcard/` or some other
path either - it might differ per device.

Instead, the `android` module which you can add to your `--requirements`
allows you to query the most commonly required paths::

      from android.storage import app_storage_path
      settings_path = app_storage_path()

      from android.storage import primary_external_storage_path
      primary_ext_storage = primary_external_storage_path()

      from android.storage import secondary_external_storage_path
      secondary_ext_storage = secondary_external_storage_path()

`app_storage_path()` gives you Android's so-called "internal storage"
which is specific to your app and cannot seen by others or the user.
It compares best to the AppData directory on Windows.

`primary_external_storage_path()` returns Android's so-called
"primary external storage", often found at `/sdcard/` and potentially
accessible to any other app.
It compares best to the Documents directory on Windows.
Requires `Permission.WRITE_EXTERNAL_STORAGE` to read and write to.

`secondary_external_storage_path()` returns Android's so-called
"secondary external storage", often found at `/storage/External_SD/`.
It compares best to an external disk plugged to a Desktop PC, and can
after a device restart become inaccessible if removed.
Requires `Permission.WRITE_EXTERNAL_STORAGE` to read and write to.

.. warning::
   Even if `secondary_external_storage_path` returns a path
   the external sd card may still not be present.
   Only non-empty contents or a successful write indicate that it is.

Read more on all the different storage types and what to use them for
in the Android documentation:

https://developer.android.com/training/data-storage/files

A note on permissions
~~~~~~~~~~~~~~~~~~~~~

Only the internal storage is always accessible with no additional
permissions. For both primary and secondary external storage, you need
to obtain `Permission.WRITE_EXTERNAL_STORAGE` **and the user may deny it.**
Also, if you get it, both forms of external storage may only allow
your app to write to the common pre-existing folders like "Music",
"Documents", and so on. (see the Android Docs linked above for details)

Runtime permissions
-------------------

With API level >= 21, you will need to request runtime permissions
to access the SD card, the camera, and other things.

This can be done through the `android` module which is *available per default*
unless you blacklist it. Use it in your app like this::

      from android.permissions import request_permissions, Permission
      request_permissions([Permission.WRITE_EXTERNAL_STORAGE])

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

To dismiss the loading screen explicitly in your code, use the `android`
module::

  from android import loadingscreen
  loadingscreen.hide_loading_screen()

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

.. _reference-label-for-android-module:

`android` for Android API access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As mentioned above, the ``android`` Python module provides a simple 
wrapper around many native Android APIS, and it is *included by default*
unless you blacklist it.

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

You should check the `Plyer documentation <https://plyer.readthedocs.io/en/stable/>`_ for details of all supported
facades (platform APIs), but as an example the following is how you
would achieve vibration as described in the Pyjnius section above::

    from plyer.vibrator import vibrate
    vibrate(10)  # in Plyer, the argument is in seconds

This is obviously *much* less verbose than with Pyjnius!


`Pyjnius` - raw lowlevel API access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

     # This one works with SDL2
     PythonActivity = autoclass('org.kivy.android.PythonActivity')

     activity = PythonActivity.mActivity

     Context = autoclass('android.content.Context')
     vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)

     vibrator.vibrate(10000)  # the argument is in milliseconds
     
Things to note here are:

- The class that must be wrapped depends on the bootstrap. This is
  because Pyjnius is using the bootstrap's java source code to get a
  reference to the current activity, which the bootstraps store in the
  ``mActivity`` static variable. This difference isn't always
  important, but it's important to know about.
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

You can check the `Pyjnius documentation <https://pyjnius.readthedocs.io/en/stable/>`_ for further details.

