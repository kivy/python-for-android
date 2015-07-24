#!/bin/bash

VERSION_bidi=${VERSION_bidi:-0.3.4}
DEPS_bidi=(python setuptools)
URL_bidi=http://pypi.python.org/packages/source/p/python-bidi/python-bidi-$VERSION_bidi.tar.gz
MD5_bidi=ce64c7d3d97264df1f84e377d145cad5
BUILD_bidi=$BUILD_PATH/bidi/$(get_directory $URL_bidi)
RECIPE_bidi=$RECIPES_PATH/bidi

function prebuild_bidi() {
	true
}

function shouldbuild_bidi() {
    if [ -d "$SITEPACKAGES_PATH/bidi" ]; then
        DO_BUILD=0
    fi
}

function build_bidi() {
    cd $BUILD_bidi
    
    push_arm

	export LDSHARED="$LIBLINK"

	try find . -iname '*.pyx' -exec $CYTHON {} \;
	try $HOSTPYTHON setup.py build_ext -v

	export PYTHONPATH=$BUILD_hostpython/Lib/site-packages
	try $BUILD_hostpython/hostpython setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages

	unset LDSHARED
	pop_arm
}

function postbuild_bidi() {
	true
}
