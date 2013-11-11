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
    true
}

function build_igraph() {
    cd $BUILD_igraph
    push_arm

    export CMD="rename 's/attributes/pyattributes/' src/attributes*"
    echo $CMD
    try $CMD
    export CMD="rename 's/random/pyrandom/' src/random*"
    echo $CMD
    try $CMD
    export CMD="cp src/* $BUILD_c_igraph/src/"
    echo $CMD
    try $CMD
    cd $BUILD_c_igraph
    try patch src/Makefile.am $RECIPE_igraph/Makefile.am.patch
    export CMD="sed -i s{BUILD_PATH{$BUILD_PATH{g src/Makefile.am"
    echo $CMD
    try $CMD
    export CPPFLAGS="-I$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/4.4.3/include -I$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/4.4.3/libs/armeabi/include -DHAVE_LOGBL"
    export CFLAGS="-I$BUILD_PATH/python-install/include/python2.7 -L$BUILD_PATH/python-install/lib"
    try ./configure --prefix="$BUILD_c_igraph" --host=arm-gnueabi --with-external-f2c
    try $MAKE
    try $MAKE install
    cd $BUILD_igraph
    export BUILDDIR="build/lib.`python $RECIPE_igraph/get_platform.py`"
    export CMD="mkdir -p $BUILDDIR"
    echo $CMD
    try $CMD
    export CMD="cp $BUILD_c_igraph/lib/libigraph.so.0.0.0 $BUILDDIR/_igraph.so"
    echo $CMD
    try $CMD
    cd $BUILD_igraph
    try $HOSTPYTHON setup.py build_scripts
    try $HOSTPYTHON setup.py install --skip-build --no-pkg-config --root $BUILD_PATH/python-install

    pop_arm
}

function postbuild_igraph() {
    true
}
