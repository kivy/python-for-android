#!/bin/bash

VERSION_libevent=${VERSION_libevent:-2.0.21-stable}
URL_libevent=https://github.com/downloads/libevent/libevent/libevent-$VERSION_libevent.tar.gz
DEPS_libevent=(python)
MD5_libevent=b2405cc9ebf264aa47ff615d9de527a2
BUILD_libevent=$BUILD_PATH/libevent/$(get_directory $URL_libevent)
RECIPE_libevent=$RECIPES_PATH/libevent

function prebuild_libevent() {
    true
}

function shouldbuild_libevent() {
    if [ -f $BUILD_libevent/build/lib/libevent.la ]; then
		DO_BUILD=0
    fi
}

function build_libevent() {
    cd $BUILD_libevent

    push_arm
    try ./configure --build=i686-pc-linux-gnu --host=arm-linux-eabi --prefix=$BUILD_libevent/build/
    try make install
    pop_arm
}

function postbuild_libevent() {
    true
}
