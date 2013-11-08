#!/bin/bash

# Recipe for igraph, a high performance graph library in C: http://igraph.org
#
# Written by Zachary Spector: https://github.com/LogicalDash/
#
# 

VERSION_c_igraph=${VERSION_c_igraph:0.6.5}

DEPS_c_igraph=()

URL_c_igraph=http://downloads.sourceforge.net/project/igraph/C%20library/0.6.5/igraph-0.6.5.tar.gz

MD5_c_igraph=5f9562263ba78b31c564d6897ff5a110

BUILD_c_igraph=$BUILD_PATH/c_igraph/$(get_directory $URL_c_igraph)

RECIPE_c_igraph=$RECIPES_PATH/c_igraph

function prebuild_c_igraph() {
    true
}

function build_c_igraph() {
    cd $BUILD_c_igraph

    push_arm

    export CPPFLAGS="-I$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/4.4.3/include -I$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/4.4.3/libs/armeabi/include"
    try ./configure --prefix="$BUILD_PATH/python-install" --libdir="$BUILD_PATH/libs" --host=arm-gnueabi --with-sysroot="$ANDROIDNDK/sources/cxx-stl/stlport/" --with-external-f2c
    try patch $BUILD_c_igraph/config.h $RECIPE_c_igraph/config.h.patch
    try $MAKE
    try $MAKE install


    pop_arm
}

function postbuild_c_igraph() {
    true
}
