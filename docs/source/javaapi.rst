Java API (pyjnius)
==================

Using `PyJNIus <https://github.com/kivy/pyjnius>`__ to access the Android API
restricts the usage to a simple call of the **autoclass** constructor function
and a second call to instantiate this class.

You can access through this method the entire Java Android API, e.g.,
the ``DisplayMetrics`` of an Android device could be fetched using the
following piece of code:

.. code-block:: python

   DisplayMetrics = autoclass('android.util.DisplayMetrics')
   metrics = DisplayMetrics()
   metrics.setToDefaults()
   self.densityDpi = metrics.densityDpi

You can access all fields and methods as described in the `Java
Android DisplayMetrics API
<http://developer.android.com/reference/android/util/DisplayMetrics.html>`__
as shown here with the method `setToDefaults()` and the field
`densityDpi`.  Before you use a view field, you should always call
`setToDefaults` to initiate to the default values of the device.

Currently only JavaMethod, JavaStaticMethod, JavaField,
JavaStaticField and JavaMultipleMethod are built into PyJNIus,
therefore such constructs like registerListener or something like this
must still be coded in Java. For this the Android module described
below is available to access some of the hardware on Android devices.

.. module:: org.renpy.android


Activity
--------

If you want the instance of the current Activity, use:

- :data:`PythonActivity.mActivity` if you are running an application
- :data:`PythonService.mService` if you are running a service

.. class:: PythonActivity

    .. data:: mInfo

        Instance of an `ApplicationInfo
        <http://developer.android.com/reference/android/content/pm/ApplicationInfo.html>`_

    .. data:: mActivity

        Instance of :class:`PythonActivity`.

    .. method:: registerNewIntentListener(NewIntentListener listener)

        Register a new instance of :class:`NewIntentListener` to be called when
        `onNewIntent
        <http://developer.android.com/reference/android/app/Activity.html#onNewIntent(android.content.Intent)>`_
        is called.

    .. method:: unregisterNewIntentListener(NewIntentListener listener)

        Unregister a previously registered listener from
        :meth:`registerNewIntentListener`

    .. method:: registerActivityResultListener(ActivityResultListener listener)

        Register a new instance of :class:`ActivityResultListener` to be called
        when `onActivityResult
        <http://developer.android.com/reference/android/app/Activity.html#onActivityResult(int,
        int, android.content.Intent)>`_ is called.

    .. method:: unregisterActivityResultListener(ActivityResultListener listener)

        Unregister a previously registered listener from
        :meth:`PythonActivity.registerActivityResultListener`

.. class:: PythonActivity_ActivityResultListener

    .. note::

        This class is a subclass of PythonActivity, so the notation will be
        ``PythonActivity$ActivityResultListener``

    Listener interface for onActivityResult. You need to implementing it,
    create an instance and use it with :meth:`PythonActivity.registerActivityResultListener`.

    .. method:: onActivityResult(int requestCode, int resultCode, Intent data)

        Method to implement

.. class:: PythonActivity_NewIntentListener

    .. note::

        This class is a subclass of PythonActivity, so the notation will be
        ``PythonActivity$NewIntentListener``

    Listener interface for onNewIntent. You need to implementing it, create
    an instance and use it with :meth:`registerNewIntentListener`.

    .. method:: onNewIntent(Intent intent)

        Method to implement


Action
------

.. class:: Action

    This module is built to deliver data to someone else.

    .. method:: send(mimetype, filename, subject, text, chooser_title)

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


Hardware
--------

.. class:: Hardware

    This module is built for accessing hardware devices of an Android device.
    All the methods are static and public, you don't need an instance.


    .. method:: vibrate(s)

       Causes the phone to vibrate for `s` seconds. This requires that your
       application have the VIBRATE permission.


    .. method:: getHardwareSensors() 

       Returns a string of all hardware sensors of an Android device where each
       line lists the informations about one sensor in the following format:

       Name=name,Vendor=vendor,Version=version,MaximumRange=maximumRange,MinDelay=minDelay,Power=power,Type=type

       For more information about this informations look into the original Java
       API for the `Sensors Class
       <http://developer.android.com/reference/android/hardware/Sensor.html>`__
       
    .. attribute:: accelerometerSensor

       This variable links to a generic3AxisSensor instance and their functions to
       access the accelerometer sensor

    .. attribute:: orientationSensor

       This variable links to a generic3AxisSensor instance and their functions to
       access the orientation sensor

    .. attribute:: magenticFieldSensor


    The following two instance methods of the generic3AxisSensor class should be
    used to enable/disable the sensor and to read the sensor


    .. method:: changeStatus(boolean enable)

       Changes the status of the sensor, the status of the sensor is enabled,
       if `enable` is true or disabled, if `enable` is false.

    .. method:: readSensor()

        Returns an (x, y, z) tuple of floats that gives the sensor reading, the
        units depend on the sensor as shown on the Java API page for
        `SensorEvent
        <http://developer.android.com/reference/android/hardware/SensorEvent.html>`_.
        The sesnor must be enabled before this function is called. If the tuple
        contains three zero values, the accelerometer is not enabled, not
        available, defective, has not returned a reading, or the device is in
        free-fall.

    .. method:: get_dpi()

        Returns the screen density in dots per inch.

    .. method:: show_keyboard()

        Shows the soft keyboard.

    .. method:: hide_keyboard()

        Hides the soft keyboard.

    .. method:: wifi_scanner_enable()

        Enables wifi scanning. 

        .. note::
        
            ACCESS_WIFI_STATE and CHANGE_WIFI_STATE permissions are required.

    .. method:: wifi_scan()

        Returns a String for each visible WiFi access point

        (SSID, BSSID, SignalLevel) 

Further Modules
~~~~~~~~~~~~~~~

Some further modules are currently available but not yet documented. Please
have a look into the code and you are very welcome to contribute to this
documentation.


