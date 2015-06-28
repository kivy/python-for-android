
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

  git clone git@github.com:inclement/python-for-android-revamp.git
  cd python-for-android
  
Or by direct download::

  wget https://github.com/inclement/python-for-android-revamp/archive/master.zip
  unzip master.zip
  cd python-for-android-revamp-master
  
Then in both cases run `python setup.py install``.

  
Basic use
---------

You can test that p4a was installed correctly by running
``python-for-android recipes``. This should print a list of all the
recipes available to be built into your APKs.

.. warning:: The below instructions are out of date, if you installed
             with pip you can replace ``python2 toolchain.py`` with
             ``python-for-android``.
             
Navigate to the ``pythonforandroid`` directory within the downloaded package.

.. note:: This will soon be replaced with a normal call to setup.py,
          but this hasn't been finished and tested yet.
          
You need to set ANDROIDSDK and ANDROIDNDK env vars to point to these.

To create a basic distribution, run .e.g::

     python2 toolchain.py create --name=testproject --bootstrap=pygame --recipes=sdl,python2
     
These arguments relate to the old python-for-android; ``name`` is the
dist name, and ``recipes`` is a list of recipes to use. The build
should proceed and eventually finish, and will print the location of
the dist.

.. note:: Compiled dists are not located in the same place as with old
          python-for-android, but instead in an OS-dependent
          location. The build process will print this location when it
          finishes.
         
To build an APK, navigate to the dist dir and run build.py just as with old p4a.

You can build an SDL2 APK similarly, first making a dist::

    python2 toolchain.py create --name=testsdl2 --bootstrap=sdl2 --recipes=sdl2,python2

This will have a build.py in the same way, but currently doesn't support many options.
