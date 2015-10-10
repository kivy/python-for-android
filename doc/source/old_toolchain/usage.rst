Usage
-----

Step 1: compile the toolchain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to compile the toolchain with only the kivy module::

    ./distribute.sh -m "kivy"

.. warning::
    Do not run the above command from `within a virtual enviroment <../faq/#too-many-levels-of-symbolic-links>`_.

After a long time, you'll get a "dist/default" directory containing
all the compiled libraries and a build.py script to package your
application using thoses libraries.

You can include other modules (or "recipes") to compile using `-m`::

    ./distribute.sh -m "openssl kivy"
    ./distribute.sh -m "pil ffmpeg kivy"

.. note::
    
    Recipes are instructions for compiling Python modules that require C extensions. 
    The list of recipes we currently have is at: 
    https://github.com/kivy/python-for-android/tree/master/recipes

You can also specify a specific version for each package. Please note
that the compilation might **break** if you don't use the default
version. Most recipes have patches to fix Android issues, and might
not apply if you specify a version. We also recommend to clean build
before changing version.::

    ./distribute.sh -m "openssl kivy==master"

Python modules that don't need C extensions don't need a recipe and
can be included this way.  From python-for-android 1.1 on, you can now
specify pure-python package into the distribution. It will use
virtualenv and pip to install pure-python modules into the
distribution. Please note that the compiler is deactivated, and will
break any module which tries to compile something. If compilation is
needed, write a recipe::

    ./distribute.sh -m "requests pygments kivy"

.. note::

   Recipes download a defined version of their needed package from the
   internet, and build from it. If you know what you are doing, and
   want to override that, you can export the env variable
   `P4A_recipe_name_DIR` and this directory will be copied and used
   instead.

Available options to `distribute.sh`::

    -d directory           Name of the distribution directory
    -h                     Show this help
    -l                     Show a list of available modules
    -m 'mod1 mod2'         Modules to include
    -f                     Restart from scratch (remove the current build)
    -u 'mod1 mod2'         Modules to update (if already compiled)

Step 2: package your application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Go to your custom Python distribution::

    cd dist/default

Use the build.py for creating the APK::

    ./build.py --package org.test.touchtracer --name touchtracer \
    --version 1.0 --dir ~/code/kivy/examples/demo/touchtracer debug

Then, the Android package (APK) will be generated at:

    bin/touchtracer-1.0-debug.apk

.. warning::

    Some files and modules for python are blacklisted by default to
    save a few megabytes on the final APK file. In case your
    applications doesn't find a standard python module, check the
    src/blacklist.txt file, remove the module you need from the list,
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
                          one of "landscape", "portrait" or "sensor".
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
    --intent-filters INTENT_FILTERS
                          Add intent-filters xml rules to AndroidManifest.xml
    --blacklist BLACKLIST
                          Use a blacklist file to match unwanted file in the
                          final APK
    --sdk SDK_VERSION     Android SDK version to use. Default to 8
    --minsdk MIN_SDK_VERSION
                          Minimum Android SDK version to use. Default to 8
    --window              Indicate if the application will be windowed

Meta-data
---------

.. versionadded:: 1.3

You can extend the `AndroidManifest.xml` with application meta-data. If you are
using external toolkits like Google Maps, you might want to set your API key in
the meta-data. You could do it like this::

    ./build.py ... --meta-data com.google.android.maps.v2.API_KEY=YOURAPIKEY

Some meta-data can be used to interact with the behavior of our internal
component.

.. list-table::
    :widths: 100 500
    :header-rows: 1

    * - Token
      - Description
    * - `surface.transparent`
      - If set to 1, the created surface will be transparent (can be used
        to add background Android widget in the background, or use accelerated
        widgets)
    * - `surface.depth`
      - Size of the depth component, default to 0. 0 means automatic, but you
        can force it to a specific value. Be warned, some old phone might not
        support the depth you want.
    * - `surface.stencil`
      - Size of the stencil component, default to 8.
    * - `android.background_color`
      - Color (32bits RGBA color), used for the background window. Usually, the
        background is covered by the OpenGL Background, unless
        `surface.transparent` is set.
