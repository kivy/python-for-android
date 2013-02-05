Usage
=====

Step 1: compile the toolchain
-----------------------------

If you want to compile the toolchain with only kivy and pyjnius module ::

    ./distribute.sh -m "pyjnius kivy"

After a long time, you'll get a "dist/default" directory containing all the compiled
libraries and build.py script to package your application using thoses
libraries.

You can include other modules (or "recipes") to compile using `-m`::

    ./distribute.sh -m "openssl pyjnius kivy"
    ./distribute.sh -m "pil ffmpeg pyjnius kivy"

For a full list, refer to :ref:`recipes`

Available options to `distribute.sh`::

    -d directory           Name of the distribution directory
    -h                     Show this help
    -l                     Show a list of available modules
    -m 'mod1 mod2'         Modules to include
    -f                     Restart from scratch (remove the current build)

Step 2: package your application
--------------------------------

Go fo your custom python distribution::

    cd dist/default

Use the build.py for creating the APK::

    ./build.py --package org.test.touchtracer --name touchtracer \
    --version 1.0 --dir ~/code/kivy/examples/demo/touchtracer debug

Then, the android package (APK) will be generated at:

    bin/touchtracer-1.0-debug.apk

.. warning::

    Some files and modules for python are blacklisted by default to
    save a few megabytes on the final apk file, in case your
    applications doesn't find a standard python module, check the
    src/blacklist.txt file remove the module you need from the list,
    and try again.

Available options to `build.py`::

    -h, --help            show this help message and exit
    --package PACKAGE     The name of the java package the project will be
                          packaged under.
    --name NAME           The human-readable name of the project.
    --version VERSION     The version number of the project. This should consist
                          of numbers and dots, and should have the same number
                          of groups of numbers as previous versions.
    --numeric-version NUMERIC_VERSION
                          The numeric version number of the project. If not
                          given, this is automatically computed from the
                          version.
    --dir DIR             The directory containing public files for the project.
    --private PRIVATE     The directory containing additional private files for
                          the project.
    --launcher            Provide this argument to build a multi-app launcher,
                          rather than a single app.
    --icon-name ICON_NAME
                          The name of the project's launcher icon.
    --orientation ORIENTATION
                          The orientation that the game will display in. Usually
                          one of "landscape" or "portrait".
    --permission PERMISSIONS
                          The permissions to give this app.
    --ignore-path IGNORE_PATH
                          Ignore path when building the app
    --icon ICON           A png file to use as the icon for the application.
    --presplash PRESPLASH
                          A jpeg file to use as a screen while the application
                          is loading.
    --install-location INSTALL_LOCATION
                          The default install location. Should be "auto",
                          "preferExternal" or "internalOnly".
    --compile-pyo         Compile all .py files to .pyo, and only distribute the
                          compiled bytecode.
    --blacklist BLACKLIST
                          Use a blacklist file to match unwanted file in the
                          final APK

    --intent-filters FILE
                          Inject the content of FILE into the activity
                          definition in the AndroidManifest.xml

