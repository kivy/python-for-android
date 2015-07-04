
Quickstart
==========

These simple steps run through the most simple procedure to create an
APK with some simple default parameters. See the :doc:`commands
documentation <commands>` for all the different commands and build
options available.

.. warning:: These instructions are quite preliminary. The
             installation and use process will become more standard in
             the near future.
             

Installation
------------

The easiest way to install is with pip. You need to have setuptools installed, but then can do::

  pip install git+https://github.com/inclement/python-for-android-revamp.git
  
This should install python-for-android (though you may need to run as root or add --user).
  
You could also install python-for-android manually, either via git::

  git clone https://github.com/inclement/python-for-android-revamp.git
  cd python-for-android
  
Or by direct download::

  wget https://github.com/inclement/python-for-android-revamp/archive/master.zip
  unzip master.zip
  cd python-for-android-revamp-master
  
Then in both cases run ``python setup.py install``.

  
Basic use
---------

python-for-android provides two executables, ``python-for-android``
and ``p4a``. These are identical and interchangeable, you can
substitute either one for the other. These instructions all use
``python-for-android``.

You can test that p4a was installed correctly by running
``python-for-android recipes``. This should print a list of all the
recipes available to be built into your APKs.

Before running any apk packaging or distribution creation, it is
essential to set some env vars. First install the Android SDK and NDK, then:

- Set the ``ANDROIDSDK`` env var to the ``/path/to/the/sdk``
- Set the ``ANDROIDNDK`` env var to the ``/path/to/the/ndk``
- Set the ``ANDROIDAPI`` to the targeted API version (or leave it
  unset to use the default of ``14``.
- Set the ``ANDROIDNDKVER`` env var to the version of the NDK
  downloaded, e.g. the current NDK is ``r10e`` (or leave it unset to
  use the default of ``r9``.

The process of setting these variables should be streamlined in the
future, these options are preliminary.

To create a basic distribution, run .e.g::

     python-for-android create --dist_name=testproject --bootstrap=pygame --requirements=sdl,python2
     
This will compile the distribution, which will take a few minutes, but
will keep you informed about its progress. The arguments relate to the
properties of the created distribution; the dist_name is an (optional)
unique identifier, and the requirements is a list of any pure Python
pypi modules, or dependencies with recipes available, that your app
depends on. The full list of builtin internal recipes can be seen with
``python-for-android recipes``.
     
.. note:: Compiled dists are not located in the same place as with old
          python-for-android, but instead in an OS-dependent
          location. The build process will print this location when it
          finishes, but you no longer need to navigate there manually
          (see below).
         
To build an APK, use the ``apk`` command::

  python-for-android apk --private /path/to/your/app --package=org.example.packagename --name="Your app name" --version=0.1
    
The arguments to ``apk`` can be anything accepted by the old
python-for-android build.py; the above is a minimal set to create a
basic app. You can see the list with ``python-for-android apk help``.

A new feature of python-for-android is that you can do all of this with just one command::

  python-for-android apk --private /home/asandy/devel/planewave_frozen/ --package=net.inclem.planewavessdl2 --name="planewavessdl2" --version=0.5 --bootstrap=sdl2 --requirements=sdl,python2 --dist_name=testproject
  
This combines the previous ``apk`` command with the arguments to
``create``, and works in exactly the same way; if no internal
distribution exists with these requirements then one is first built,
before being used to package the APK. When the command is run again,
the build step is skipped and the previous dist re-used. 

Using this method you don't have to worry about whether a dist exists,
though it is recommended to use a different ``dist_name`` for each
project unless they have precisely the same requirements.

You can build an SDL2 APK similarly, creating a dist as follows::

    python2 toolchain.py create --name=testsdl2 --bootstrap=sdl2 --recipes=sdl2,python2

You can then make an APK in the same way, but this is more
experimental and doesn't support as much customisation yet.

python-for-android also has commands to list internal information
about distributions available, to export or symlink these (they come
with a standalone APK build script), and in future will also support
features including binary download to avoid the manual compilation
step.

See the :doc:`commands` documentation for full details of available
functionality.
