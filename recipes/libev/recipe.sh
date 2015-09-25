#!/bin/bash

URL_libev=http://localhost:8080/packages/libev-4.20.zip
DEPS_libev=(python)
BUILD_libev=$BUILD_PATH/libev/$(get_directory $URL_libev)
RECIPE_libev=$RECIPES_PATH/libev

function prebuild_libev() {
    true
}

function shouldbuild_libev() {
    if [ -f $BUILD_libev/build/lib/libev.la ]; then
		DO_BUILD=0
    fi
}

function build_libev() {
    cd $BUILD_libev

    push_arm
    try ./configure --build=i686-pc-linux-gnu --host=arm-linux-eabi --prefix=$BUILD_libev/build/
    try make install
    pop_arm
    
}

function postbuild_libev() {
    true
}
