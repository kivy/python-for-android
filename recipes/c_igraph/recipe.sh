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
    if [ ! -e $BUILD_c_igraph/.patched ]; then {
            try patch $BUILD_c_igraph/src/Makefile.am $RECIPE_c_igraph/Makefile.am.patch;
            try cp -f $RECIPE_c_igraph/arith.h $BUILD_c_igraph/src/f2c/arith.h;
            try patch $BUILD_c_igraph/src/f2c/sysdep1.h $RECIPE_c_igraph/sysdep1.h.patch;
            try patch $BUILD_c_igraph/src/f2c/uninit.c $RECIPE_c_igraph/uninit.c.patch;
            touch $BUILD_c_igraph/.patched;
        }
    fi
}

function shouldbuild_c_igraph() {
    if [ -e $BUILD_c_igraph/.built ]; then
        export DO_BUILD=0;
    fi
}

function build_c_igraph() {
    cd $BUILD_c_igraph

    push_arm
    if [ ! -e $BUILD_c_igraph/config.h ]; then
        export OLD_CPPFLAGS="$CPPFLAGS";
        export CPPFLAGS="$CPPFLAGS -I$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/4.4.3/include -I$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/4.4.3/libs/armeabi/include -L$ANDROIDNDK/platforms/android-$ANDROIDAPI/arch-arm/usr/lib";
        try ./configure --prefix="$BUILD_PATH/python-install" --build=i686-pc-linux-gnu --host=arm-linux-eabi;
        try patch $BUILD_c_igraph/config.h $RECIPE_c_igraph/config.h.patch;
        export CPPFLAGS="$OLD_CPPFLAGS";
    fi


    try $MAKE
    try $MAKE install

    pop_arm
    touch .built
}

function postbuild_c_igraph() {
    true
}
