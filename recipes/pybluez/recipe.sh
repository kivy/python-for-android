#!/bin/bash

VERSION_pyblues=
URL_pybluez=https://dl.dropboxusercontent.com/u/26205750/pybluez.tar.gz
DEPS_pybluez=(python setuptools)
BUILD_pybluez=$BUILD_PATH/pybluez/$(get_directory $URL_pybluez)
RECIPE_pybluez=$RECIPE_PATH/pybluez


function prebuild_pybluez() {

    cd $BUILD_pybluez

    if [ -f .patched ]; then
        return
    fi

    try patch setup.py  < $RECIPE_pybluez/patches/patch-android.patch

    touch .patched
}

function build_pybluez() {

    if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/pybluez"  ]; then
        return
    fi
    
    cd $BUILD_pybluez

    push_arm
    
    export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
    export LDSHARED="$LIBLINK"
    
    #cythonize
    try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
    try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

    unset LDSHARED

    pop_arm

}

function postbuild_pybluez() {
    true
}
