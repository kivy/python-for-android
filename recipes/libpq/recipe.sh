#!/bin/bash

VERSION_libpq=${VERSION_libpq:-9.3.5}
URL_libpq=http://ftp.postgresql.org/pub/source/v$VERSION_libpq/postgresql-$VERSION_libpq.tar.bz2
DEPS_libpq=(python)
MD5_libpq=5059857c7d7e6ad83b6d55893a121b59
BUILD_libpq=$BUILD_PATH/libpq/$(get_directory $URL_libpq)
RECIPE_libpq=$RECIPES_PATH/libpq

function prebuild_libpq() {
    cd $BUILD_libpq
    if [ -f .patched ]; then
        return
    fi
    # http://www.postgresql.org/message-id/4ECCD3D9.3040505@bernawebdesign.ch
    try patch -p1 < $RECIPE_libpq/patches/libpq.patch
    touch .patched
}

function shouldbuild_libpq() {
    if [ -f "$BUILD_libpq/src/interfaces/libpq/libpq.so" ]; then
        DO_BUILD=0
    fi
}

function build_libpq() {
    cd $BUILD_libpq

    push_arm

    try ./configure --without-readline --host=arm-linux
    try make submake-libpq
    try cp -a $BUILD_libpq/src/interfaces/libpq/libpq.a $LIBS_PATH

    pop_arm

}

function postbuild_libpq() {
    true
}
