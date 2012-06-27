Android Python module
=====================

Python for android project include a python module named "android". This module is designed to give you an access to the Android API. As for today, the module is very limited, and waiting for contribution to wrap more Android API.

Example
-------

::

    import android

    # activate the vibrator
    android.vibrate(1)

    # read screen dpi
    print android.get_dpi()

How it's working
----------------

The whole Android API is accessible in Java. Their is no native or extensible
way to access it from Python. The schema for accessing to their API is::

    [1] Cython -> [2] C JNI -> [3] Java

#. ``android.pyx`` is written in `Cython <http://cython.org/>`_: a language
   with typed informations, very close to Python, that generate Python
   extension. It's easier to write in Cython than CPython, and it's linked
   directly to the part 2.
#. ``android_jni.c`` is defining simple c methods that access to Java
   interfaces using JNI layer.
#. The last part contain the Java code that will be called from the JNI stuff.

All the source code is available at:

    https://github.com/kivy/python-for-android/tree/master/recipes/android/src


API
---

android
~~~~~~~

.. module:: android

.. function:: check_pause()

    This should be called on a regular basis to check to see if Android
    expects the game to pause. If it return true, the game should call
    :func:`android.wait_for_resume()`, after persisting its state as necessary.

.. function:: wait_for_resume()

    This function should be called after :func:`android.check_pause()` returns
    true. It does not return until Android has resumed from the pause. While in
    this function, Android may kill a game without further notice.

.. function:: map_key(keycode, keysym)

    This maps between an android keycode and a python keysym. The android
    keycodes are available as constants in the android module.

.. function:: vibrate(s)

    Causes the phone to vibrate for `s` seconds. This requires that your
    application have the VIBRATE permission.

.. function:: accelerometer_enable(enable)

    Enables (if `enable` is true) or disables the device's accelerometer.

.. function:: accelerometer_reading()

    Returns an (x, y, z) tuple of floats that gives the accelerometer reading,
    in meters per second squared. See `this page
    <http://developer.android.com/reference/android/hardware/SensorEvent.html>`_
    for a description of the coordinate system. The accelerometer must be
    enabled before this function is called. If the tuple contains three zero
    values, the accelerometer is not enabled, not available, defective, has not
    returned a reading, or the device is in free-fall.

.. function:: get_dpi()

    Returns the screen density in dots per inch.

.. function:: show_keyboard()

    Shows the soft keyboard.

.. function:: hide_keyboard()

    Hides the soft keyboard.

.. function:: wifi_scanner_enable()

    Enables wifi scanning. ACCESS_WIFI_STATE and CHANGE_WIFI_STATE permissions
    required.

.. function:: wifi_scan()

    Returns tuple of (SSID, BSSID, SignalLevel) for each visible WiFi access
    point.

.. function:: action_send(mimetype, filename, subject, text, chooser_title)

    Deliver data to someone else. This method is a wrapper around `ACTION_SEND
    <http://developer.android.com/reference/android/content/Intent.html#ACTION_SEND>`_

    :Parameters:
        `mimetype`: str
            Must be a valid mimetype, that represent the content to sent.
        `filename`: str, default to None
            (optional) Name of the file to attach. Must be a absolute path.
        `subject`: str, default to None
            (optional) Default subject
        `text`: str, default to None
            (optional) Content to send.
        `chooser_title`: str, default to None
            (optional) Title of the android chooser window, default to 'Send email...'

    Sending a simple hello world text::

        android.action_send('text/plain', text='Hello world',
            subject='Test from python')

    Sharing an image file::

        # let's say you've make an image in /sdcard/image.png
        android.action_send('image/png', filename='/sdcard/image.png')

    Sharing an image with a default text too::

        android.action_send('image/png', filename='/sdcard/image.png',
            text='Hi,\n\tThis is my awesome image, what do you think about it ?')

android_mixer
~~~~~~~~~~~~~

.. module:: android_mixer

The android_mixer module contains a subset of the functionality in found
in the `pygame.mixer <http://www.pygame.org/docs/ref/mixer.html>`_ module. It's
intended to be imported as an alternative to pygame.mixer, using code like: ::

   try:
       import pygame.mixer as mixer
   except ImportError:
       import android_mixer as mixer

Note that if you're using `kivy.core.audio
<http://kivy.org/docs/api-kivy.core.audio.html>`_ module, you don't have to do
anything, all is automatic.

The android_mixer module is a wrapper around the Android MediaPlayer
class. This allows it to take advantage of any hardware acceleration
present, and also eliminates the need to ship codecs as part of an
application.

It has several differences from the pygame mixer:

* The init and pre_init methods work, but are ignored - Android chooses
  appropriate setting automatically.

* Only filenames and true file objects can be used - file-like objects
  will probably not work.

* Fadeout does not work - it causes a stop to occur.

* Looping is all or nothing, there's no way to choose the number of
  loops that occur. For looping to work, the
  :func:`android_mixer.periodic` function should be called on a
  regular basis.

* Volume control is ignored.

* End events are not implemented.

* The mixer.music object is a class (with static methods on it),
  rather than a module. Calling methods like :func:`mixer.music.play`
  should work.

.. note::

    The android_mixer module hasn't been tested much, and so bugs may be
    present.

android_billing
~~~~~~~~~~~~~~~

.. module:: android_billing

This billing module give an access to the `In-App Billing <http://developer.android.com/guide/google/play/billing/billing_overview.html>`_:

#. `Setup a test accounts <http://developer.android.com/guide/google/play/billing/billing_admin.html#billing-testing-setup>`, and get your Public Key
#. Export your public key::

    export BILLING_PUBKEY="Your public key here"

#. `Setup some In-App product <http://developer.android.com/guide/google/play/billing/billing_admin.html>`_ to buy. Let's say you've created a product with the id "org.kivy.gopremium"

#. In your application, you can use the billing module like this::


    from android_billing import BillingService
    from kivy.clock import Clock

    class MyBillingService(object):

        def __init__(self):
            super(MyBillingService, self).__init__()

            # Start the billing service, and attach our callback
            self.service = BillingService(billing_callback)

            # Start a clock to check billing service message every seconds
            Clock.schedule_interval(self.service.check, 1)

        def billing_callback(self, action, *largs):
            '''Callback that will receive all the event from the Billing service
            '''
            if action == BillingService.BILLING_ACTION_ITEMSCHANGED:
                items = largs[0]
                if 'org.kivy.gopremium' in items:
                    print 'Congratulation, you have a premium acess'
                else:
                    print 'Unfortunately, you dont have premium access'

        def buy(self, sku):
            # Method to buy something.
            self.service.buy(sku)

        def get_purchased_items(self):
            # Return all the items purchased
            return self.service.get_purchased_items()

#. To initiate a in-app purchase, just call the buy method::

    # Note: start the service at the start, and never twice!
    bs = MyBillingService()
    bs.buy('org.kivy.gopremium')

    # Later, when you get the notification that items have been changed, you
    # can still check all the items you bought:
    print bs.get_purchased_items()
    {'org.kivy.gopremium': {'qt: 1}}

#. You'll receive all the notification about the billing process in the callback.

#. Last step, create your application with `--with-billing $BILLING_PUBKEY`::

    ./build.py ... --with-billing $BILLING_PUBKEY

