
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

https://developer.android.com/training/data-storage

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


Observing Activity result
~~~~~~~~~~~~~~~~~~~~~~~~~

.. module:: android.activity

The default PythonActivity has a observer pattern for `onActivityResult <https://developer.android.com/reference/android/app/Activity#onActivityResult(int, int, android.content.Intent)>`_ and `onNewIntent <https://developer.android.com/reference/android/app/Activity.html#onNewIntent(android.content.Intent)>`_.

.. function:: bind(eventname=callback, ...)

    This allows you to bind a callback to an Android event:
    - ``on_new_intent`` is the event associated to the onNewIntent java call
    - ``on_activity_result`` is the event associated to the onActivityResult java call

    .. warning::

        This method is not thread-safe. Call it in the mainthread of your app. (tips: use kivy.clock.mainthread decorator)

.. function:: unbind(eventname=callback, ...)

    Unregister a previously registered callback with :func:`bind`.

Example::

    # This example is a snippet from an NFC p2p app implemented with Kivy.

    from android import activity

    def on_new_intent(self, intent):
        if intent.getAction() != NfcAdapter.ACTION_NDEF_DISCOVERED:
            return
        rawmsgs = intent.getParcelableArrayExtra(NfcAdapter.EXTRA_NDEF_MESSAGES)
        if not rawmsgs:
            return
        for message in rawmsgs:
            message = cast(NdefMessage, message)
            payload = message.getRecords()[0].getPayload()
            print('payload: {}'.format(''.join(map(chr, payload))))

    def nfc_enable(self):
        activity.bind(on_new_intent=self.on_new_intent)
        # ...

    def nfc_disable(self):
        activity.unbind(on_new_intent=self.on_new_intent)
        # ...


Activity lifecycle handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Android ``Application`` class provides the `ActivityLifecycleCallbacks
<https://developer.android.com/reference/android/app/Application.ActivityLifecycleCallbacks>`_
interface where callbacks can be registered corresponding to `activity
lifecycle
<https://developer.android.com/guide/components/activities/activity-lifecycle>`_
changes. These callbacks can be used to implement logic in the Python app when
the activity changes lifecycle states.

Note that some of the callbacks are not useful in the Python app. For example,
an `onActivityCreated` callback will never be run since the the activity's
`onCreate` callback will complete before the Python app is running. Similarly,
saving instance state in an `onActivitySaveInstanceState` callback will not be
helpful since the Python app doesn't have access to the restored instance
state.

.. function:: register_activity_lifecycle_callbacks(callbackname=callback, ...)

    This allows you to bind a callbacks to Activity lifecycle state changes.
    The callback names correspond to ``ActivityLifecycleCallbacks`` method
    names such as ``onActivityStarted``. See the `ActivityLifecycleCallbacks
    <https://developer.android.com/reference/android/app/Application.ActivityLifecycleCallbacks>`_
    documentation for names and function signatures for the callbacks.

.. function:: unregister_activity_lifecycle_callbacks(instance)

    Unregister a ``ActivityLifecycleCallbacks`` instance previously registered
    with :func:`register_activity_lifecycle_callbacks`.

Example::

    from android.activity import register_activity_lifecycle_callbacks

    def on_activity_stopped(activity):
        print('Activity is stopping')

    register_activity_lifecycle_callbacks(
        onActivityStopped=on_activity_stopped,
    )


Receiving Broadcast message
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. module:: android.broadcast

Implementation of the android `BroadcastReceiver
<https://developer.android.com/reference/android/content/BroadcastReceiver.html>`_.
You can specify the callback that will receive the broadcast event, and actions
or categories filters.

.. class:: BroadcastReceiver

    .. warning::

        The callback will be called in another thread than the main thread. In
        that thread, be careful not to access OpenGL or something like that.

    .. method:: __init__(callback, actions=None, categories=None)

        :param callback: function or method that will receive the event. Will
                         receive the context and intent as argument.
        :param actions: list of strings that represent an action.
        :param categories: list of strings that represent a category.

        For actions and categories, the string must be in lower case, without the prefix::

            # In java: Intent.ACTION_HEADSET_PLUG
            # In python: 'headset_plug'

    .. method:: start()

        Register the receiver with all the actions and categories, and start
        handling events.

    .. method:: stop()

        Unregister the receiver with all the actions and categories, and stop
        handling events.

Example::

    class TestApp(App):

        def build(self):
            self.br = BroadcastReceiver(
                self.on_broadcast, actions=['headset_plug'])
            self.br.start()
            # ...

        def on_broadcast(self, context, intent):
            extras = intent.getExtras()
            headset_state = bool(extras.get('state'))
            if headset_state:
                print('The headset is plugged')
            else:
                print('The headset is unplugged')

        # Don't forget to stop and restart the receiver when the app is going
        # to pause / resume mode

        def on_pause(self):
            self.br.stop()
            return True

        def on_resume(self):
            self.br.start()

Runnable
~~~~~~~~

.. module:: android.runnable

:class:`Runnable` is a wrapper around the Java `Runnable
<https://developer.android.com/reference/java/lang/Runnable.html>`_ class. This
class can be used to schedule a call of a Python function into the
`PythonActivity` thread.

Example::

    from android.runnable import Runnable

    def helloworld(arg):
        print 'Called from PythonActivity with arg:', arg

    Runnable(helloworld)('hello')

Or use our decorator::

    from android.runnable import run_on_ui_thread

    @run_on_ui_thread
    def helloworld(arg):
        print 'Called from PythonActivity with arg:', arg

    helloworld('arg1')


This can be used to prevent errors like:

    - W/System.err( 9514): java.lang.RuntimeException: Can't create handler
      inside thread that has not called Looper.prepare()
    - NullPointerException in ActivityThread.currentActivityThread()

.. warning::

    Because the python function is called from the PythonActivity thread, you
    need to be careful about your own calls.


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

You can check the `Pyjnius documentation <https://pyjnius.readthedocs.io/en/latest/>`_ for further details.

