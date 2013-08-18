#!/bin/bash

VERSION_gevent=0.13.8
URL_gevent=https://pypi.python.org/packages/source/g/gevent/gevent-$VERSION_gevent.tar.gz
DEPS_gevent=(libevent greenlet)
MD5_gevent=ca9dcaa7880762d8ebbc266b11252960
BUILD_gevent=$BUILD_PATH/gevent/$(get_directory $URL_gevent)
RECIPE_gevent=$RECIPES_PATH/gevent

function prebuild_gevent() {
    true
}

function build_gevent() {
    cd $BUILD_gevent

    if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/gevent" ]; then
        return
    fi

    push_arm
    export CFLAGS="$CFLAGS -I$BUILD_libevent/build/include"
    export LDFLAGS="$LDFLAGS -L$LIBS_PATH -L$BUILD_libevent/build/lib/"

    try $BUILD_PATH/python-install/bin/python.host setup.py install -O2
    pop_arm
}

function postbuild_gevent() {
    true
}
