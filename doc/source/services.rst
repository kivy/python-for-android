Services
========

python-for-android supports the use of Android Services, background
tasks running in separate processes. These are the closest Android
equivalent to multiprocessing on e.g. desktop platforms, and it is not
possible to use normal multiprocessing on Android. Services are also
the only way to run code when your app is not currently opened by the user.

Services must be declared when building your APK. Each one
will have its own main.py file with the Python script to be run.
Please note that python-for-android explicitly runs services as separated
processes by having a colon ":" in the beginning of the name assigned to
the ``android:process`` attribute of the ``AndroidManifest.xml`` file.
This is not the default behavior, see `Android service documentation
<https://developer.android.com/guide/topics/manifest/service-element>`__.
You can communicate with the service process from your app using e.g.
`osc <https://pypi.python.org/pypi/python-osc>`__ or (a heavier option)
`twisted <https://twistedmatrix.com/trac/>`__.

Service creation
----------------

There are two ways to have services included in your APK.

Service folder
~~~~~~~~~~~~~~

This is the older method of handling services. It is
recommended to use the second method (below) where possible.

Create a folder named ``service`` in your app directory, and add a
file ``service/main.py``. This file should contain the Python code
that you want the service to run.

To start the service, use the :code:`start_service` function from the
:code:`android` module (you may need to add ``android`` to your app
requirements)::

    import android
    android.start_service(title='service name',
                          description='service description',
                          arg='argument to service')

.. _arbitrary_scripts_services:

Arbitrary service scripts
~~~~~~~~~~~~~~~~~~~~~~~~~

This method is recommended for non-trivial use of services as it is
more flexible, supporting multiple services and a wider range of
options.

To create the service, create a python script with your service code
and add a :code:`--service=myservice:PATH_TO_SERVICE_PY` argument
when calling python-for-android, or in buildozer.spec, a
:code:`services = myservice:PATH_TO_SERVICE_PY` [app] setting.

The ``myservice`` name before the colon is the name of the service
class, via which you will interact with it later. 

The ``PATH_TO_SERVICE_PY`` is the relative path to the service entry point (like ``services/myservice.py``)

You can optionally specify the following parameters:
 - :code:`:foreground` for launching a service as an Android foreground service
 - :code:`:sticky` for launching a service that gets restarted by the Android OS on exit/error

Full command with all the optional parameters included would be: 
:code:`--service=myservice:services/myservice.py:foreground:sticky`

You can add multiple
:code:`--service` arguments to include multiple services, or separate
them with a comma in buildozer.spec, all of which you will later be
able to stop and start from your app.

To run the services (i.e. starting them from within your main app
code), you must use PyJNIus to interact with the java class
python-for-android creates for each one, as follows::

    from jnius import autoclass
    service = autoclass('your.package.domain.package.name.ServiceMyservice')
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    argument = ''
    service.start(mActivity, argument)

Here, ``your.package.domain.package.name`` refers to the package identifier
of your APK.

If you are using buildozer, the identifier is set by the ``package.name``
and ``package.domain`` values in your buildozer.spec file.
The name of the service is ``ServiceMyservice``, where ``Myservice``
is the name specied by one of the ``services`` values, but with the first
letter upper case. 

If you are using python-for-android directly, the identifier is set by the ``--package``
argument to python-for-android. The name of the service is ``ServiceMyservice``,
where ``Myservice`` is the identifier that was previously passed to the ``--service``
argument, but with the first letter upper case. You must also pass the
``argument`` parameter even if (as here) it is an empty string. If you
do pass it, the service can make use of this argument.

The service argument is made available to your service via the
'PYTHON_SERVICE_ARGUMENT' environment variable. It is exposed as a simple
string, so if you want to pass in multiple values, we would recommend using
the json module to encode and decode more complex data.
::

    from os import environ
    argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')
    
To customize the notification icon, title, and text use three optional
arguments to service.start()::

    service.start(mActivity, 'small_icon', 'title', 'content' , argument)

Where 'small_icon' is the name of an Android drawable or mipmap resource,
and 'title' and 'content' are strings in the notification.

Services support a range of options and interactions not yet
documented here but all accessible via calling other methods of the
``service`` reference.

.. note::

    The app root directory for Python imports will be in the app
    root folder even if the service file is in a subfolder. To import from
    your service folder you must use e.g.  ``import service.module``
    instead of ``import module``, if the service file is in the
    ``service/`` folder.

Service auto-restart
~~~~~~~~~~~~~~~~~~~~

It is possible to make services restart automatically when they exit by
calling ``setAutoRestartService(True)`` on the service object.
The call to this method should be done within the service code::

    from jnius import autoclass
    PythonService = autoclass('org.kivy.android.PythonService')
    PythonService.mService.setAutoRestartService(True)
    
Service auto-start
~~~~~~~~~~~~~~~~~~

To automatically start the service on boot, you need to add signals inside ``AndroidManifest.xml`` that Android sends to applications on boot. 
Create file ``receivers.xml`` and write this code::

    <receiver android:name=".MyBroadcastReceiver" android:enabled="true" android:exported="true">
        <intent-filter>
            <action android:name="android.intent.action.BOOT_COMPLETED" />
            <action android:name="android.intent.action.QUICKBOOT_POWERON" />
            <action android:name="com.htc.intent.action.QUICKBOOT_POWERON" />
        </intent-filter>
    </receiver> 
    
    
Next step set path to this file in ``buildozer.spec``, set setting ``android.extra_manifest_application_xml`` code::

    android.extra_manifest_application_xml = %(source.dir)s/xml/receivers.xml
    
Then need create ``MyBroadcastReceiver.java``, code::

    package com.heattheatr.kivy_service_test;

    import android.content.BroadcastReceiver;
    import android.content.Intent;
    import android.content.Context;
    import org.kivy.android.PythonActivity;

    import java.lang.reflect.Method;

    import com.heattheatr.kivy_service_test.ServiceTest;

    public class MyBroadcastReceiver extends BroadcastReceiver {

        public MyBroadcastReceiver() {

        }

        // Start app.
        public void start_app(Context context, Intent intent) {
            Intent ix = new Intent(context, PythonActivity.class);
            ix.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(ix);
        }

        // Start service.
        public void service_start(Context context, Intent intent) {
            String package_root = context.getFilesDir().getAbsolutePath();
            String app_root =  package_root + "/app";
            Intent ix = new Intent(context, ServiceTest.class);
            ix.putExtra("androidPrivate", package_root);
            ix.putExtra("androidArgument", app_root);
            ix.putExtra("serviceEntrypoint", "service.py");
            ix.putExtra("pythonName", "test");
            ix.putExtra("pythonHome", app_root);
            ix.putExtra("pythonPath", package_root);
            ix.putExtra("serviceStartAsForeground", "true");
            ix.putExtra("serviceTitle", "ServiceTest");
            ix.putExtra("serviceDescription", "ServiceTest");
            ix.putExtra("pythonServiceArgument", app_root + ":" + app_root + "/lib");
            ix.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startService(ix);
        }

        // Stop service.
        public void service_stop(Context context, Intent intent) {
            Intent intent_stop = new Intent(context, ServiceTest.class);

            context.stopService(intent_stop);
        }

        // Sinals reciver.
        public void onReceive(Context context, Intent intent) {
            switch (intent.getAction()) {
                case Intent.ACTION_BOOT_COMPLETED:
                    System.out.println("python MyBroadcastReceiver.java 
                               MyBroadcastReceiver.class onReceive.method: ACTION_BOOT_COMPLETED");
                    this.service_start(context, intent);
                    break;
                default:
                   break;
            }
        }
    }
    
This code start ``service.py`` from ``buildozer.spec`` when get signal ``ACTION_BOOT_COMPLETED``::
    
    services = Test:./service.py:foreground
    
For example ``service.py``::

    import os
    from time import sleep

    from jnius import cast
    from jnius import autoclass

    PythonService = autoclass('org.kivy.android.PythonService')
    CurrentActivityService = cast("android.app.Service", PythonService.mService)

    while True:
        print("python service running.....", CurrentActivityService.getPackageName(), os.getpid())
        sleep(10)
        
Name out service will be ``ServiceTest``, prefix ``Service`` + ``Test`` from ``services = Test:./service.py:foreground``. 

You can see how it work in test `project <https://github.com/dvjdjvu/kivy_service_test>`__.
