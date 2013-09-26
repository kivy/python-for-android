#!/bin/bash

VERSION_msgpack=${VERSION_msgpack:-0.3.0}
URL_msgpack=https://pypi.python.org/packages/source/m/msgpack-python/msgpack-python-$VERSION_msgpack.tar.gz
DEPS_msgpack=(python setuptools)
MD5_msgpack=10dec96c90992b0f6e38bdf0cc5a8e79
BUILD_msgpack=$BUILD_PATH/msgpack/$(get_directory $URL_msgpack)
RECIPE_msgpack=$RECIPES_PATH/msgpack

function prebuild_msgpack() {
    true
}

function build_msgpack() {
    cd $BUILD_msgpack

    if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/msgpack" ]; then
        return
    fi

    push_arm

    # fake try to be able to cythonize generated files
    $BUILD_PATH/python-install/bin/python.host setup.py build_ext
    try find . -iname '*.pyx' -exec cython {} \;
    try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v

    try find build/lib.* -name "*.o" -exec $STRIP {} \;

    export PYTHONPATH=$BUILD_PATH/hostpython/Python-2.7.2/Lib/site-packages
    try $BUILD_PATH/hostpython/Python-2.7.2/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

    pop_arm
}

function postbuild_msgpack() {
    true
}
