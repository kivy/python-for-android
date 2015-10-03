Customize your distribution
---------------------------

The basic layout of a distribution is::

    AndroidManifest.xml     - (*) android manifest (generated from templates)
    assets/
        private.mp3         - (*) fake package that will contain all the python installation
        public.mp3          - (*) fake package that will contain your application
    bin/                    - contain all the apk generated from build.py
    blacklist.txt           - list of file patterns to not include in the APK
    buildlib/               - internals libraries for build.py
    build.py                - build script to use for packaging your application
    build.xml               - (*) build settings (generated from templates)
    default.properties      - settings generated from your distribute.sh
    libs/                   - contain all the compiled libraries
    local.properties        - settings generated from your distribute.sh
    private/                - private directory containing all the python files
        lib/                  this is where you can remove or add python libs.
            python2.7/        by default, some modules are already removed (tests, idlelib, ...)
    project.properties      - settings generated from your distribute.sh
    python-install/         - the whole python installation, generated from distribute.sh
                              not included in the final package.
    res/                    - (*) android resource (generated from build.py)
    src/                    - Java bootstrap
    templates/              - Templates used by build.py

    (*): Theses files are automatically generated from build.py, don't change them directly !


