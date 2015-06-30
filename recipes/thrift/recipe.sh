#!/bin/bash

VERSION_thrift=${VERSION_thrift:-0.9.2}
URL_thrift=https://pypi.python.org/packages/source/t/thrift/thrift-$VERSION_thrift.tar.gz
DEPS_thrift=(python setuptools)
MD5_thrift=91f1c224c46a257bb428431943387dfd
BUILD_thrift=$BUILD_PATH/thrift/$(get_directory $URL_thrift)
RECIPE_thrift=$RECIPES_PATH/thrift

function prebuild_thrift() {
    true
}

function shouldbuild_thrift() {
    if [ -d "$SITEPACKAGES_PATH/thrift" ]; then
		DO_BUILD=0
    fi
}

function build_thrift() {
    cd $BUILD_thrift

    push_arm

    # fake try to be able to cythonize generated files
    $HOSTPYTHON setup.py build_ext
    try find . -iname '*.pyx' -exec $CYTHON {} \;
    try $HOSTPYTHON setup.py build_ext -v

    try find build/lib.* -name "*.o" -exec $STRIP {} \;

    export PYTHONPATH=$BUILD_PATH/hostpython/Python-2.7.2/Lib/site-packages
    try $BUILD_PATH/hostpython/Python-2.7.2/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

    pop_arm
}

function postbuild_thrift() {
    true
}
