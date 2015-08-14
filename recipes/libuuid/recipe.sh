#!/bin/bash

VERSION_libuuid=${VERSION_libuuid:-1.0.3}
URL_libuuid=http://downloads.sourceforge.net/project/libuuid/libuuid-${VERSION_libuuid}.tar.gz
DEPS_libuuid=()
BUILD_libuuid=$BUILD_PATH/libuuid/$(get_directory $URL_libuuid)
RECIPE_libuuid=$RECIPES_PATH/libuuid

function prebuild_libuuid() {
    true
}

function shouldbuild_libuuid() {
    # if [ -f $BUILD_libuuid/build/lib/libuuid.la ]; then
    #     	DO_BUILD=0
    # fi
    true
}

function build_libuuid() {
    cd $BUILD_libuuid

    push_arm
    try ./configure --build=i686-pc-linux-gnu --host=arm-linux-eabi --prefix=$BUILD_libuuid/build/
    try make install
    libtool --finish $BUILD_libuuid/build/
    pop_arm
}

function postbuild_libuuid() {
    true
}
