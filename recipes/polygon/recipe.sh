#!/bin/bash

URL_polygon=https://bitbucket.org/jraedler/polygon2/get/ec07628ee633.zip
DEPS_polygon=(python)
MD5_polygon=
BUILD_polygon=$BUILD_PATH/polygon/$(get_directory $URL_polygon)
RECIPE_polygon=$RECIPES_PATH/polygon

function prebuild_polygon() {
    true
}

function shouldbuild_polygon() {
    if [ -d "$SITEPACKAGES_PATH/polygon" ]; then
        DO_BUILD=0
    fi
}

function build_polygon() {
    cd $BUILD_polygon
        echo "helllooo"
    push_arm

    export LDSHARED="$LIBLINK"

    try find . -iname '*.pyx' -exec $CYTHON {} \;
    try $HOSTPYTHON setup.py build_ext -v
    try find build/lib.* -name "*.o" -exec $STRIP {} \;

    export PYTHONPATH=$BUILD_hostpython/Lib/site-packages
        echo $BUILD_hostpython/hostpython
    try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

    unset LDSHARED
    pop_arm
}

function postbuild_polygon() {
    true
}
