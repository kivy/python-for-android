#!/bin/bash

VERSION_libgmp=${VERSION_libgmp:-6.0.0a}
URL_libgmp=https://gmplib.org/download/gmp/gmp-${VERSION_libgmp}.tar.xz
DEPS_libgmp=()
BUILD_libgmp=$BUILD_PATH/libgmp/$(get_directory $URL_libgmp)
RECIPE_libgmp=$RECIPES_PATH/libgmp

function prebuild_libgmp() {
    true
}

function shouldbuild_libgmp() {
    true
}

function build_libgmp() {
    cd $BUILD_libgmp

    push_arm
    try ./configure --build=i686-pc-linux-gnu --host=arm-linux-eabi --prefix=$BUILD_libgmp/build/
    #try make check
    try make install
    libtool --finish $BUILD_libgmp/build/
    pop_arm
}

function postbuild_libgmp() {
    true
}
