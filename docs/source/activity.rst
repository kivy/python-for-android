Python Activity
===============

Our android activity is named `org.renpy.android.PythonActivity` for a normal
application, and `org.renpy.android.PythonService` for a service.

Accessing to the Python Activity API
------------------------------------

Instead of wrapping all the java part into python extension, we think it's less
work for us and easy for you to directly use Pyjnius::

    from jnius import autoclass
    PythonActivity = autoclass('org.renpy.android.PythonActivity')

You have the class object of our Python Activity, and can access to anything from the API. If you want the instance of it, use:

- :data:`PythonActivity.mActivity` if you are running an application
- :data:`PythonService.mService` if you are running a service



`PythonActivity` API
--------------------

.. class:: PythonActivity

    .. data:: mInfo

        Instance of an `ApplicationInfo
        <http://developer.android.com/reference/android/content/pm/ApplicationInfo.html>`_

    .. data:: mActivity

        Instance of :class:`PythonActivity`.

    .. method:: registerNewIntentListener(NewIntentListener listener)

        Register a new instance of :class:`NewIntentListener` to be called when `onNewIntent <http://developer.android.com/reference/android/app/Activity.html#onNewIntent(android.content.Intent)>`_ is called.

    .. method:: unregisterNewIntentListener(NewIntentListener listener)

        Unregister a previously registered listener from :meth:`registerNewIntentListener`

    .. method:: registerActivityResultListener(ActivityResultListener listener)

        Register a new instance of :class:`ActivityResultListener` to be called when `onActivityResult <http://developer.android.com/reference/android/app/Activity.html#onActivityResult(int, int, android.content.Intent)>`_ is called.

    .. method:: unregisterActivityResultListener(ActivityResultListener listener)

        Unregister a previously registered listener from :meth:`PythonActivity.registerActivityResultListener`

    .. class:: NewIntentListener

        Listener interface for onNewIntent. You need to implementing it, create
        an instance and use it with :meth:`registerNewIntentListener`.

        .. method:: onNewIntent(Intent intent)

            Method to implement

    .. class:: ActivityResultListener

        Listener interface for onActivityResult. You need to implementing it,
        create an instance and use it with :meth:`PythonActivity.registerActivityResultListener`.

        .. method:: onActivityResult(int requestCode, int resultCode, Intent data)

            Method to implement

