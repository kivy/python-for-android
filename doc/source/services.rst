Services
========

python-for-android supports the use of Android Services, background
tasks running in separate processes. These are the closest Android
equivalent to multiprocessing on e.g. desktop platforms, and it is not
possible to use normal multiprocessing on Android. Services are also
the only way to run code when your app is not currently opened by the user.

Services must be declared when building your APK. Each one
will have its own main.py file with the Python script to be run. You
can communicate with the service process from your app using e.g. `osc
<https://pypi.python.org/pypi/python-osc>`__ or (a heavier option)
`twisted <https://twistedmatrix.com/trac/>`__.

Service creation
----------------

There are two ways to have services included in your APK.

Service folder
~~~~~~~~~~~~~~

This basic method works with both the new SDL2 and old Pygame
bootstraps. It is recommended to use the second method (below) where
possible.

Create a folder named ``service`` in your app directory, and add a
file ``service/main.py``. This file should contain the Python code
that you want the service to run.

To start the service, use the :code:`start_service` function from the
:code:`android` module (included automatically with the Pygame
bootstrap, you must add it to the requirements manually with SDL2 if
you wish to use this method)::

    import android
    android.start_service(title='service name',
                          description='service description',
                          arg='argument to service')

.. _arbitrary_scripts_services:

Arbitrary service scripts
~~~~~~~~~~~~~~~~~~~~~~~~~

.. note:: This service method is *not supported* by the Pygame bootstrap.

This method is recommended for non-trivial use of services as it is
more flexible, supporting multiple services and a wider range of
options.

To create the service, create a python script with your service code
and add a :code:`--service=myservice:/path/to/myservice.py` argument
when calling python-for-android. The ``myservice`` name before the
colon is the name of the service class, via which you will interact
with it later. You can add multiple
:code:`--service` arguments to include multiple services, which you
will later be able to stop and start from your app.

To run the services (i.e. starting them from within your main app
code), you must use PyJNIus to interact with the java class
python-for-android creates for each one, as follows::

    from jnius import autoclass
    service = autoclass('your.package.name.ServiceMyservice')
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    argument = ''
    service.start(mActivity, argument)

Here, ``your.package.name`` refers to the package identifier of your
APK as set by the ``--package`` argument to python-for-android, and
the name of the service is ``ServiceYourservicename``, in which
``Yourservicename`` is the identifier passed to the ``--service``
argument with the first letter upper case. You must also pass the
``argument`` parameter even if (as here) it is an empty string. If you
do pass it, the service can make use of this argument.

Services support a range of options and interactions not yet
documented here but all accessible via calling other methods of the
``service`` reference.

.. note::

    The app root directory for Python imports will be in the app
    root folder even if the service file is in a subfolder. To import from
    your service folder you must use e.g.  ``import service.module``
    instead of ``import module``, if the service file is in the
    ``service/`` folder.
