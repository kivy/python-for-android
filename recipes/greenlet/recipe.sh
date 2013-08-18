#!/bin/bash

VERSION_greenlet=0.4.1
URL_greenlet=https://pypi.python.org/packages/source/g/greenlet/greenlet-$VERSION_greenlet.zip
https://github.com/downloads/greenlet/greenlet/greenlet-$VERSION_greenlet.tar.gz
DEPS_greenlet=(python)
MD5_greenlet=c2deda75bdda59c38cae12a77cc53adc
BUILD_greenlet=$BUILD_PATH/greenlet/$(get_directory $URL_greenlet)
RECIPE_greenlet=$RECIPES_PATH/greenlet

function prebuild_greenlet() {
    true
}

function build_greenlet() {
    cd $BUILD_greenlet

    if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/greenlet.so" ]; then
        return
    fi

    push_arm

    try $BUILD_PATH/python-install/bin/python.host setup.py install -O2
    pop_arm
}

function postbuild_greenlet() {
    true
}
