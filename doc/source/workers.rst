Workers
=======

python-for-android supports worker tasks using `WorkManager
<https://developer.android.com/topic/libraries/architecture/workmanager>`_.
``WorkManager`` tasks are the recommended way to perform both one-time
and recurring work with current Android. Starting with Android 12,
worker tasks will also be required to replace foreground services in
some cases.

Each worker runs tasks in a service declared in the
``AndroidManifest.xml`` file. This is managed by python-for-android with
a service generated from the application package. The worker service is
specified to run in a separate process since python-for-android does not
support running multiple Python interpreters in the same process.

Worker creation
---------------

To create the worker, create a python script with your worker code and
add a ``--worker=myworker:PATH_TO_WORKER_PY`` argument when calling
python-for-android.

The ``myworker`` name before the colon is in the names of the worker and
worker service classes, via which you will interact with it later.

The ``PATH_TO_WORKER_PY`` is the relative path to the worker entry point
(like ``workers/myworker.py``)

You can add multiple ``--worker`` arguments to include multiple workers,
all of which you will later be able to stop and start from your app.

Running workers
---------------

To run the workers (i.e. starting them from within your main app code),
you must use PyJNIus to interact with the Java class python-for-android
creates for each one. First, you need to create a work request using the
``buildInputData`` helper function which configures the work to run in
the appropriate service class::

    from jnius import autoclass

    worker = autoclass('your.package.domain.package.name.MyworkerWorker')
    OneTimeWorkRequestBuilder = autoclass('androidx.work.OneTimeWorkRequest$Builder')
    argument = ''
    data = worker.buildInputData(argument)
    request = OneTimeWorkRequestBuilder(worker._class).setInputData(data).build()

Here, ``your.package.domain.package.name`` refers to the package
identifier of your APK. The identifier is set by the ``--package``
argument to python-for-android. The name of the worker is
``MyworkerWorker``, where ``Myworker`` is the identifier that was
previously passed to the ``--worker`` argument, but with the first
letter upper case. You must also pass the ``argument`` parameter even if
(as here) it is an empty string or `None`. If you do pass it, the
service can make use of this argument.

The argument is made available to your worker via the
'PYTHON_SERVICE_ARGUMENT' environment variable. It is exposed as a
simple string, so if you want to pass in multiple values, we would
recommend using the json module to encode and decode more complex data.
::

    from os import environ
    argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')

Now the work request needs to be enqueued in the application's
`WorkManager
<https://developer.android.com/reference/androidx/work/WorkManager>`_
instance::

    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    WorkManager = autoclass('androidx.work.WorkManager')
    work_manager = WorkManager.getInstance(mActivity)
    work_manager.enqueue(request)

Enqueuing a work request is asynchronous and returns an `Operation
<https://developer.android.com/reference/androidx/work/Operation>`_. To
block until the request has been queued, wait for the state to resolve::

    operation = work_manager.enqueue(request)
    operation.getResult().get()

Once the work request has been queued, information about the request
such as its current state can be requested from ``WorkManager``::

    request_id = request.getId()
    work_info = work_manager.getWorkInfoById(request_id).get()
    state = work_info.getState()
    print('Work request state:', state.toString())
    if state.isFinished():
        print('Work request has completed')

.. note::

    The app root directory for Python imports will be in the app root
    folder even if the worker file is in a subfolder. If the worker is
    in the ``worker/`` folder, it must be imported with ``import
    worker.module`` rather than ``import module``.

Worker progress
~~~~~~~~~~~~~~~

A worker can send intermediate progress data for the work request that
can be retrieved in the activity. From the worker script, use the
``setProgressAsync`` method from the worker class instance::

    from jnius import autoclass

    mWorker = autoclass('your.package.domain.package.name.MyworkerWorker').mWorker
    DataBuilder = autoclass('androidx.work.Data$Builder')

    data = DataBuilder().putInt('PROGRESS', 50).build()
    mWorker.setProgressAsync(data)

The progress can be retrieved in the activity from the work request
information::

    request_id = request.getId()
    work_info = work_manager.getWorkInfoById(request_id).get()
    progress = work_info.getProgress().getInt('PROGRESS', 0)
    print('Work request {}% complete'.format(progress))

.. note::

    At present, there is no method to return output data for the work
    request. The work is either succeeded or failed based on the exit
    status of the worker script.
