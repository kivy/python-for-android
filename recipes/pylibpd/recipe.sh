#!/bin/bash

VERSION_pylibpd=
DEPS_pylibpd=(python)
URL_pylibpd=https://github.com/libpd/libpd/archive/master.zip
MD5_pylibpd=
BUILD_pylibpd=$BUILD_PATH/pylibpd/$(get_directory $URL_pylibpd)
RECIPE_pylibpd=$RECIPES_PATH/pylibpd

function prebuild_pylibpd() {
    # Apply thread removal patch
    cd $BUILD_pylibpd/python
    if [ -f .patched ]; then
        return
    fi
    try patch -p1 < $RECIPE_pylibpd/patches/threadfix.patch
    touch .patched
}

function build_pylibpd() {
    cd $BUILD_pylibpd/python
    push_arm
    try $BUILD_PATH/python-install/bin/python.host setup.py build
    try $BUILD_PATH/python-install/bin/python.host setup.py install -O2
    try $BUILD_PATH/python-install/bin/python.host setup.py clean
    pop_arm
}

# function called after all the compile have been done
function postbuild_pylibpd() {
    true
}
