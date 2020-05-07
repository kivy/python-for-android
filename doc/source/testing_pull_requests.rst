Testing an python-for-android pull request
==========================================

In order to test a pull request, we recommend to consider the following points:

  #. of course, check if the overall thing makes sense
  #. is the CI passing? if not what specifically fails
  #. is it working locally at compile time?
  #. is it working on device at runtime?

This document will focus on the third point:
`is it working locally at compile time?` so we will give some hints about how
to proceed in order to create a local copy of the pull requests and build an
apk. We expect that the contributors has enough criteria/knowledge to perform
the other steps mentioned, so let's begin...

To create an apk from a python-for-android pull request we contemplate three
possible scenarios:

  - using python-for-android commands directly from the pull request files
    that we want to test, without installing it (the recommended way for most
    of the test cases)
  - installing python-for-android using the github's branch of the pull request
  - using buildozer and a custom app

We will explain the first two methods using one of the distributed
python-for-android test apps and we assume that you already have the
python-for-android dependencies installed. For the `buildozer` method we also
expect that you already have a a properly working app to test and a working
installation/configuration of `buildozer`. There is one step that it's shared
with all the testing methods that we propose in here...we named it
`Common steps`.


Common steps
^^^^^^^^^^^^
The first step to do it's to get a copy of the pull request, we can do it of
several ways, and that it will depend of the circumstances but all the methods
presented here will do the job, so...

Fetch the pull request by number
--------------------------------
For the example, we will use `1901` for the example) and the pull request
branch that we will use is `feature-fix-numpy`, then you will use a variation
of the following git command:
`git fetch origin pull/<#>/head:<local_branch_name>`, e.g.:

.. code-block:: bash

    git fetch upstream pull/1901/head:feature-fix-numpy

.. note:: Notice that we fetch from `upstream`, since that is the original
          project, where the pull request is supposed to be

.. tip:: The amount of work of some users maybe worth it to add his remote
       to your fork's git configuration, to do so with the imaginary
       github user `Obi-Wan Kenobi` which nickname is `obiwankenobi`, you
       will do:

          .. code-block:: bash

              git remote add obiwankenobi https://github.com/obiwankenobi/python-for-android.git

       And to fetch the pull request branch that we put as example, you
       would do:

          .. code-block:: bash

              git fetch obiwankenobi
              git checkout obiwankenobi/feature-fix-numpy


Clone the pull request branch from the user's fork
--------------------------------------------------
Sometimes you may prefer to use directly the fork of the user, so you will get
the nickname of the user who created the pull request, let's take the same
imaginary user than before `obiwankenobi`:

    .. code-block:: bash

        git clone -b feature-fix-numpy \
            --single-branch \
            https://github.com/obiwankenobi/python-for-android.git \
            p4a-feature-fix-numpy

Here's the above command explained line by line:

- `git clone -b feature-fix-numpy`: we tell git that we want to clone the
  branch named `feature-fix-numpy`
- `--single-branch`: we tell git that we only want that branch
- `https://github.com/obiwankenobi/python-for-android.git`: noticed the
  nickname of the user that created the pull request: `obiwankenobi` in the
  middle of the line? that should be changed as needed for each pull
  request that you want to test
- `p4a-feature-fix-numpy`: the name of the cloned repository, so we can
  have multiple clones of different prs in the same folder

.. note:: You can view the author/branch information looking at the
          subtitle of the pull request, near the pull request status (expected
          an `open` status)

Using python-for-android commands directly from the pull request files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Enter inside the directory of the cloned repository in the above
  step and run p4a command with proper args, e.g. (to test an modified
  `pycryptodome` recipe)

.. code-block:: bash

    cd p4a-feature-fix-numpy
    PYTHONPATH=. python3 -m pythonforandroid.toolchain apk \
        --private=testapps/on_device_unit_tests/test_app \
        --dist-name=dist_unit_tests_app_pycryptodome \
        --package=org.kivy \
        --name=unit_tests_app_pycryptodome \
        --version=0.1 \
        --requirements=sdl2,pyjnius,kivy,python3,pycryptodome \
        --ndk-dir=/media/DEVEL/Android/android-ndk-r20 \
        --sdk-dir=/media/DEVEL/Android/android-sdk-linux \
        --android-api=27 \
        --arch=arm64-v8a \
        --permission=VIBRATE \
        --debug

Things that you should know:


    - The example above will build an test app we will make use of the files of
      the `on device unit tests` test app but we don't use the setup
      file to build it so we must tell python-for-android what we want via
      arguments
    - be sure to at least edit the following arguments when running the above
      command, since the default set in there it's unlikely that match your
      installation:

          - `--ndk-dir`: An absolute path to your android's NDK dir
          - `--sdk-dir`: An absolute path to your android's SDK dir
          - `--debug`: this one enables the debug mode of python-for-android,
            which will show all log messages of the build. You can omit this
            one but it's worth it to be mentioned, since this it's useful to us
            when trying to find the source of the problem when things goes
            wrong
    - The apk generated by the above command should be located at the root of
      of the cloned repository, were you run the command to build the apk
    - The testapps distributed with python-for-android are located at
      `testapps` folder under the main folder project
    - All the builds of python-for-android are located at
      `~/.local/share/python-for-android`
    - You should have a downloaded copy of the android's NDK and SDK

Installing python-for-android using the github's branch of the pull request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Enter inside the directory of the cloned repository mentioned in
  `Common steps` and install it via pip, e.g.:

.. code-block:: bash

    cd p4a-feature-fix-numpy
    pip3 install . --upgrade --user

- Now, go inside the `testapps/on_device_unit_tests` directory (we assume that
  you still are inside the cloned repository)

.. code-block:: bash

    cd testapps/on_device_unit_tests

- Run the build of the apk via the freshly installed copy of python-for-android
  by running a similar command than below

.. code-block:: bash

    python3 setup.py apk \
        --ndk-dir=/media/DEVEL/Android/android-ndk-r20 \
        --sdk-dir=/media/DEVEL/Android/android-sdk-linux \
        --android-api=27 \
        --arch=arm64-v8a \
        --debug


Things that you should know:

    - In the example above, we override some variables that are set in
      `setup.py`, you could also override them by editing this file
    - be sure to at least edit the following arguments when running the above
      command, since the default set in there it's unlikely that match your
      installation:

        - `--ndk-dir`: An absolute path to your android's NDK dir
        - `--sdk-dir`: An absolute path to your android's SDK dir

.. tip:: if you don't want to mess up with the system's python, you could do
          the same steps but inside a virtualenv

.. warning:: Once you finish the pull request tests remember to go back to the
             master or develop versions of python-for-android, since you just
             installed the python-for-android files of the `pull request`

Using buildozer with a custom app
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Edit your `buildozer.spec` file. You should search for the key
  `p4a.source_dir` and set the right value so in the example posted in
  `Common steps` it would look like this::

    p4a.source_dir = /home/user/p4a_pull_requests/p4a-feature-fix-numpy

- Run you buildozer command as usual, e.g.::

    buildozer android debug p4a --dist-name=dist-test-feature-fix-numpy

.. note:: this method has the advantage, can be run without installing the
          pull request version of python-for-android nor the android's
          dependencies but has one problem...when things goes wrong you must
          determine if it's a buildozer issue or a python-for-android one

.. warning:: Once you finish the pull request tests remember to comment/edit
             the `p4a.source_dir` constant that you just edited to test the
             pull request

.. tip:: this method it's useful for developing pull requests since you can
         edit `p4a.source_dir` to point to your python-for-android fork and you
         can test any branch you want only switching branches with:
         `git checkout <branch-name>` from inside your python-for-android fork
