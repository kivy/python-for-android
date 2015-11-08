#!/bin/bash

VERSION_pylibpd=${VERSION_pylibpd:-master}
DEPS_pylibpd=(python)
URL_pylibpd=https://github.com/libpd/libpd/archive/$VERSION_pylibpd.zip
MD5_pylibpd=
BUILD_pylibpd=$BUILD_PATH/pylibpd/$(get_directory $URL_pylibpd)
RECIPE_pylibpd=$RECIPES_PATH/pylibpd
GIT_pylibpd=https://github.com/libpd/libpd

function prebuild_pylibpd() {
    # Clone recursively libpd repository
    rm -rf $BUILD_pylibpd
    git clone --recursive $GIT_pylibpd $BUILD_pylibpd
    # Apply thread removal patch
    cd $BUILD_pylibpd/python
    if [ -f .patched ]; then
        return
    fi
    try patch -p1 < $RECIPE_pylibpd/patches/threadfix.patch
    touch .patched
    # Apply Makefile patch
    cd $BUILD_pylibpd
    if [ -f .patched ]; then
        return
    fi
    try patch < $RECIPE_pylibpd/patches/makefilefix.patch
    touch .patched
}

function shouldbuild_pylibpd() {
	if [ -d "$SITEPACKAGES_PATH/pylibpd" ]; then
		DO_BUILD=0
	fi
}

function build_pylibpd() {
    push_arm
    cd $BUILD_pylibpd
    try make
    cd python 
    try $HOSTPYTHON setup.py build
    try $HOSTPYTHON setup.py install -O2
    try $HOSTPYTHON setup.py clean
    pop_arm
}

# function called after all the compile have been done
function postbuild_pylibpd() {
    true
}
