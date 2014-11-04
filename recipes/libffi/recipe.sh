#!/bin/bash

VERSION_libffi=${VERSION_libffi:-3.1}
URL_libffi=https://github.com/atgreen/libffi/archive/v$VERSION_libffi.tar.gz
#DEPS_libffi=(python)
MD5_libffi=663d72841855334ff65b16d8d5decfe5
BUILD_libffi=$BUILD_PATH/libffi/$(get_directory $URL_libffi)
RECIPE_libffi=$RECIPES_PATH/libffi

function prebuild_libffi() {
    true
}

function shouldbuild_libffi() {
    if [ -f $BUILD_libffi/build/lib/libffi.la ]; then
		DO_BUILD=0
    fi
}

function build_libffi() {
    cd $BUILD_libffi

    push_arm
    export GREP_OPTIONS=''
    try ./autogen.sh
    try ./configure --build=i686-pc-linux-gnu --host=arm-linux-eabi --prefix=$BUILD_libffi/build/
    try make install
    pop_arm
}

function postbuild_libffi() {
    true
}
