Python API
==========

The Python for Android project includes a Python module called
``android`` which consists of multiple parts that are mostly there to
facilitate the use of the Java API.

This module is not designed to be comprehensive. Most of the Java API
is also accessible with PyJNIus, so if you can't find what you need
here you can try using the Java API directly instead.


Android (``android``)
---------------------

.. module:: android

.. function:: check_pause()

    This should be called on a regular basis to check to see if Android
    expects the application to pause. If it returns true, the app should call
    :func:`android.wait_for_resume()`, after storing its state as necessary.

.. function:: wait_for_resume()

    This function should be called after :func:`android.check_pause()` and returns
    true. It does not return until Android has resumed from the pause. While in
    this function, Android may kill the app without further notice.

.. function:: map_key(keycode, keysym)

    This maps an android keycode to a python keysym. The android
    keycodes are available as constants in the android module.


Activity (``android.activity``)
-------------------------------

.. module:: android.activity

The default PythonActivity has a observer pattern for `onActivityResult <http://developer.android.com/reference/android/app/Activity.html#onActivityResult(int, int, android.content.Intent)>`_ and `onNewIntent <http://developer.android.com/reference/android/app/Activity.html#onNewIntent(android.content.Intent)>`_.

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
            print 'payload: {}'.format(''.join(map(chr, payload)))

    def nfc_enable(self):
        activity.bind(on_new_intent=self.on_new_intent)
        # ...

    def nfc_disable(self):
        activity.unbind(on_new_intent=self.on_new_intent)
        # ...


Billing (``android.billing``)
-----------------------------

.. module:: android.billing

This billing module gives an access to the `In-App Billing <http://developer.android.com/guide/google/play/billing/billing_overview.html>`_:

#. `Setup a test account <http://developer.android.com/guide/google/play/billing/billing_admin.html#billing-testing-setup>`_, and get your Public Key
#. Export your public key::

    export BILLING_PUBKEY="Your public key here"

#. `Setup some In-App product <http://developer.android.com/guide/google/play/billing/billing_admin.html>`_ to buy. Let's say you've created a product with the id "org.kivy.gopremium"

#. In your application, you can use the ``billing`` module like this::


    from android.billing import BillingService
    from kivy.clock import Clock

    class MyBillingService(object):

        def __init__(self):
            super(MyBillingService, self).__init__()

            # Start the billing service, and attach our callback
            self.service = BillingService(billing_callback)

            # Start a clock to check billing service message every second
            Clock.schedule_interval(self.service.check, 1)

        def billing_callback(self, action, *largs):
            '''Callback that will receive all the events from the Billing service
            '''
            if action == BillingService.BILLING_ACTION_ITEMSCHANGED:
                items = largs[0]
                if 'org.kivy.gopremium' in items:
                    print "Congratulations, you have a premium acess"
                else:
                    print "Unfortunately, you don't have premium access"

        def buy(self, sku):
            # Method to buy something.
            self.service.buy(sku)

        def get_purchased_items(self):
            # Return all the items purchased
            return self.service.get_purchased_items()

#. To initiate an in-app purchase, just call the ``buy()`` method::

    # Note: start the service at the start, and never twice!
    bs = MyBillingService()
    bs.buy('org.kivy.gopremium')

    # Later, when you get the notification that items have been changed, you
    # can still check all the items you bought:
    print bs.get_purchased_items()
    {'org.kivy.gopremium': {'qt: 1}}

#. You'll receive all the notifications about the billing process in the callback.

#. Last step, create your application with ``--with-billing $BILLING_PUBKEY``::

    ./build.py ... --with-billing $BILLING_PUBKEY


Broadcast (``android.broadcast``)
---------------------------------

.. module:: android.broadcast

Implementation of the android `BroadcastReceiver
<http://developer.android.com/reference/android/content/BroadcastReceiver.html>`_.
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
                print 'The headset is plugged'
            else:
                print 'The headset is unplugged'

        # Don't forget to stop and restart the receiver when the app is going
        # to pause / resume mode

        def on_pause(self):
            self.br.stop()
            return True

        def on_resume(self):
            self.br.start()


Mixer (``android.mixer``)
-------------------------

.. module:: android.mixer

The `android.mixer` module contains a subset of the functionality in found
in the `pygame.mixer <http://www.pygame.org/docs/ref/mixer.html>`_ module. It's
intended to be imported as an alternative to pygame.mixer, using code like: ::

   try:
       import pygame.mixer as mixer
   except ImportError:
       import android.mixer as mixer

Note that if you're using the `kivy.core.audio
<http://kivy.org/docs/api-kivy.core.audio.html>`_ module, you don't have to do
anything, it is all automatic.

The `android.mixer` module is a wrapper around the Android MediaPlayer
class. This allows it to take advantage of any hardware acceleration
present, and also eliminates the need to ship codecs as part of an
application.

It has several differences with the pygame mixer:

* The init() and pre_init() methods work, but are ignored - Android chooses
  appropriate settings automatically.

* Only filenames and true file objects can be used - file-like objects
  will probably not work.

* Fadeout does not work - it causes a stop to occur.

* Looping is all or nothing, there is no way to choose the number of
  loops that occur. For looping to work, the
  :func:`android.mixer.periodic` function should be called on a
  regular basis.

* Volume control is ignored.

* End events are not implemented.

* The mixer.music object is a class (with static methods on it),
  rather than a module. Calling methods like :func:`mixer.music.play`
  should work.


Runnable (``android.runnable``)
-------------------------------

.. module:: android.runnable

:class:`Runnable` is a wrapper around the Java `Runnable
<http://developer.android.com/reference/java/lang/Runnable.html>`_ class. This
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



Service (``android.service``)
-----------------------------

Services of an application are controlled through the class :class:`AndroidService`.

.. module:: android.service

.. class:: AndroidService(title, description)

    Run ``service/main.py`` from the application directory as a service.

    :param title: Notification title, default to 'Python service'
    :param description: Notification text, default to 'Kivy Python service started'
    :type title: str
    :type description: str

    .. method:: start(arg)

        Start the service.

        :param arg: Argument to pass to a service, through the environment variable
                    ``PYTHON_SERVICE_ARGUMENT``. Defaults to ''
        :type arg: str

    .. method:: stop()

        Stop the service.

Application activity part example, ``main.py``:

.. code-block:: python

  from android import AndroidService

  ...

   class ServiceExample(App):

    ...

       def start_service(self):
           self.service = AndroidService('Sevice example', 'service is running')
           self.service.start('Hello From Service')

       def stop_service(self):
           self.service.stop()

Application service part example, ``service/main.py``:

.. code-block:: python

   import os
   import time

   # get the argument passed
   arg = os.getenv('PYTHON_SERVICE_ARGUMENT')

   while True:
       # this will print 'Hello From Service' continually, even when the application is switched
       print arg
       time.sleep(1)

