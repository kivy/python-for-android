#!/bin/bash

# Recipe for the Python interface to igraph, a high-performance graph library in C: http://igraph.org/
#
# Written by Zachary Spector: https://github.com/LogicalDash/

VERSION_igraph=${VERSION_igraph:0.6.5}

DEPS_igraph=(python c_igraph)

URL_igraph=http://pypi.python.org/packages/source/p/python-igraph/python-igraph-0.6.5.tar.gz

MD5_igraph=c626585baf003af855c0dc4eec0c9baa

BUILD_igraph=$BUILD_PATH/igraph/$(get_directory $URL_igraph)

RECIPE_igraph=$RECIPES_PATH/igraph


function prebuild_igraph() {
    true
}

function shouldbuild_igraph() {
    true
}

function build_igraph() {
    cd $BUILD_igraph
    push_arm

    patch setup.py $RECIPE_igraph/setup.py.patch
    try $HOSTPYTHON setup.py build_ext -p arm-gnueabi -L "$BUILD_PATH/libs" -I "$BUILD_PATH/python-install/include/igraph/" install --no-pkg-config --root $BUILD_PATH/python-install

    pop_arm
}

function postbuild_igraph() {
    true
}
