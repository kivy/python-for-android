#!/bin/bash

# Recipe for the Python interface to igraph, a high-performance graph library in C: http://igraph.org/
#
# Written by Zachary Spector: https://github.com/LogicalDash/

VERSION_igraph=${VERSION_igraph:0.6.5}

DEPS_igraph=(c_igraph python)

URL_igraph=http://pypi.python.org/packages/source/p/python-igraph/python-igraph-0.6.5.tar.gz

MD5_igraph=c626585baf003af855c0dc4eec0c9baa

BUILD_igraph=$BUILD_PATH/igraph/$(get_directory $URL_igraph)

RECIPE_igraph=$RECIPES_PATH/igraph


function prebuild_igraph() {
    if [ ! -f "$BUILD_igraph/.patched" ]; then
        try patch $BUILD_igraph/setup.py $RECIPE_igraph/setup.py.patch
        try patch $BUILD_igraph/setup.cfg $RECIPE_igraph/setup.cfg.patch
        touch $BUILD_igraph/.patched
    fi
}

function shouldbuild_igraph() {
    if [ -e $BUILD_igraph/.built ]; then
        export DO_BUILD=0;
    fi
}

function build_igraph() {
    cd $BUILD_igraph
    push_arm

    try $HOSTPYTHON setup.py build_ext -I"$BUILD_PATH/python-install/include/igraph:$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/4.4.3/libs/armeabi/include" -L"$BUILD_PATH/python-install/lib:$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/4.4.3/libs/armeabi" -l gnustl_static -p arm-gnueabi install

    pop_arm
    touch .built
}

function postbuild_igraph() {
    true
}
