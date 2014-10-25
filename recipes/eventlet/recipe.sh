#!/bin/bash

VERSION_eventlet=${VERSION_eventlet:-0.15.2}
URL_eventlet=https://pypi.python.org/packages/source/e/eventlet/eventlet-$VERSION_eventlet.tar.gz
DEPS_eventlet=(libevent greenlet)
MD5_eventlet=c5b0217cc1da6fcf4bcf6957df57f3cd
BUILD_eventlet=$BUILD_PATH/eventlet/$(get_directory $URL_eventlet)
RECIPE_eventlet=$RECIPES_PATH/eventlet

function prebuild_eventlet() {
    # TODO: patch setup.py to use distutils instead of setuptools
    true
}

function shouldbuild_eventlet() {
	if [ -d "$SITEPACKAGES_PATH/eventlet" ]; then
		DO_BUILD=0
	fi
}

function build_eventlet() {
    cd $BUILD_eventlet

    push_arm
    export CFLAGS="$CFLAGS -I$BUILD_libevent/build/include"
    export LDFLAGS="$LDFLAGS -L$LIBS_PATH -L$BUILD_libevent/build/lib/"

    try $HOSTPYTHON setup.py install -O2
    pop_arm
}

function postbuild_eventlet() {
    true
}
